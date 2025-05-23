import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import uuid

# Assuming SFTContentItem will be imported from core_models
from ..core_models.sft_content_item import SFTContentItem
import mistune

class SFTParser:
    """
    Parses SFT (Superfunctional Training System) markdown documents
    to extract structured content items.
    """
    def __init__(self, sft_root_dir: str):
        self.sft_root_dir = Path(sft_root_dir).resolve()
        if not self.sft_root_dir.is_dir():
            raise ValueError(f"SFT root directory not found: {sft_root_dir}")
        
        self.excluded_dirs = {"AI_version", "Resources", "Updates", ".git", ".vscode"}
        self.ref_tag_regex = re.compile(r"\{ref:\s*([^}]+)\}")
        self.heading_regex = re.compile(r"^(#{1,3})\s+(.*)") # For H1, H2, H3
        self.ai_context_start_regex = re.compile(r"<!-- AI\.CONTEXT:\s*(.*?)-->", re.IGNORECASE)
        self.ai_context_end_regex = re.compile(r"<!-- AI\.CONTEXT\.END:\s*.*?-->", re.IGNORECASE)
        self.markdown_parser = mistune.create_markdown(renderer=None) # Creates AST

    def _extract_references_from_text(self, text: str) -> List[str]:
        if not text: return []
        return list(set(self.ref_tag_regex.findall(text)))

    def _discover_markdown_files(self) -> List[Path]:
        markdown_files = []
        for item in self.sft_root_dir.rglob('*.md'):
            if item.is_file():
                is_excluded = False
                for part in item.relative_to(self.sft_root_dir).parts:
                    if part in self.excluded_dirs:
                        is_excluded = True
                        break
                if not is_excluded:
                    markdown_files.append(item)
        return markdown_files

    def _parse_metadata_block(self, content: str) -> Optional[Dict[str, Any]]:
        metadata_match = re.search(r"<!-- AI\.METADATA\s*\n(.*?)\n\s*-->", content, re.DOTALL | re.IGNORECASE)
        if not metadata_match: return None
        metadata_str = metadata_match.group(1)
        metadata = {}
        for line in metadata_str.splitlines():
            line = line.strip()
            if not line: continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower().replace("_", "")
                value = parts[1].strip()
                if value.startswith('"') and value.endswith('"'): value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"): value = value[1:-1]
                if key == "references" and value.startswith("[") and value.endswith("]"):
                    metadata[key] = [ref.strip().strip('"\'') for ref in value[1:-1].split(',')]
                else: metadata[key] = value
        return metadata

    def _render_node_to_markdown(self, node: Dict[str, Any]) -> str:
        """
        Simple helper to get a raw text representation from an AST node.
        Mistune v3 AST structure:
        - Paragraphs: {'type': 'paragraph', 'children': [{'type': 'text', 'text': 'content'}]}
        - Lists: {'type': 'list', 'children': [list_item_nodes], 'ordered': False/True, 'start': Optional[int]}
        - List Items: {'type': 'list_item', 'children': [paragraph_nodes_usually]} (Mistune v3)
                      (Mistune v2 was {'type': 'item', 'children': [...]})
        - Text: {'type': 'text', 'text': 'content'} (Mistune v3) or {'type': 'text', 'raw': 'content'} (Mistune v2)
        - Strong/Emphasis: {'type': 'strong', 'children': [{'type': 'text', ...}]}
        This function aims to reconstruct a readable string, not perfect markdown.
        It's primarily used to get the textual content of a single AST node for SFTContentItem.raw_content.
        For complex nodes like list_item, we want only its direct text, not deeply nested content.
        """
        node_type = node.get('type')

        if node_type == 'text':
            return node.get('text', node.get('raw', ''))
        
        # For block_html, block_code, thematic_break, etc., their 'raw' or 'text' content is usually sufficient.
        raw_text = node.get('raw')
        if raw_text is not None:
            return raw_text
        if node_type == 'block_code': # Mistune v3 uses 'text' for code content
             return node.get('text', '')

        # For other block types (paragraph, heading, list_item children that are not lists themselves),
        # concatenate the text from their direct children (which are usually inline elements).
        # Avoid deep recursion for 'raw_content' of a single item.
        # The SFTParser._create_items_from_ast will handle creating child SFTContentItems for nested block structures.
        if 'children' in node and isinstance(node['children'], list):
            # If this node itself is a list or list_item, we are trying to get its textual representation.
            # For a list_item, we only want its immediate text, not text from nested lists.
            # For a list (list_block), its raw_content will be built from its list_item children's raw_content by _create_items_from_ast.
            # So, if we are rendering a list_item, we only process its non-list children.
            
            content_parts = []
            for child in node['children']:
                child_type = child.get('type')
                if node_type == 'list_item' and child_type == 'list': # If rendering a list_item, skip its nested lists for raw_content
                    content_parts.append("[nested list placeholder]") # Or just skip
                    continue
                content_parts.append(self._render_node_to_markdown(child))
            return "".join(content_parts)
        
        return ""


    def _create_items_from_ast(self, 
                               ast_nodes: List[Dict[str, Any]], 
                               parent_item_id: str, 
                               source_file_path: str,
                               starting_order: int) -> Tuple[List[SFTContentItem], int]:
        created_items: List[SFTContentItem] = []
        current_order = starting_order

        # Debug: Print incoming AST nodes
        print(f"    DEBUG _create_items_from_ast: parent_id={parent_item_id}, num_ast_nodes={len(ast_nodes if ast_nodes else [])}")
        if ast_nodes:
            for i, n in enumerate(ast_nodes):
                print(f"      DEBUG _create_items_from_ast: AST Node {i} type={n.get('type') if isinstance(n, dict) else type(n)}")

        if not isinstance(ast_nodes, list): # Guard against non-list input (e.g. if a node's children isn't a list)
            return created_items, current_order

        for node in ast_nodes:
            if not isinstance(node, dict): continue # AST nodes should be dicts

            node_type = node.get('type')
            # Reconstruct a semblance of raw markdown for this specific node for SFTContentItem.raw_content
            # This is tricky; Mistune v3 doesn't always provide 'raw' for block elements easily.
            # _render_node_to_markdown gives a concatenated text version.
            # For list_item, we want its direct text only for its own raw_content.
            # Nested lists within it will become child SFTContentItems.
            raw_node_content = self._render_node_to_markdown(node)

            item_type_str = f"ast_{node_type}" # Default item_type
            component_name_for_item = None

            if node_type == 'paragraph':
                item_type_str = "paragraph"
            elif node_type == 'list':
                item_type_str = "list_block" # Changed from 'list' to avoid confusion with Python list
                # For a list block, its raw_content is the concatenation of its items' content.
                # The component_name could be derived if the list has a preceding title, but that's complex.
            elif node_type == 'list_item': # Mistune v3 uses 'list_item'
                item_type_str = "list_item"
            elif node_type == 'heading': # Mistune parses sub-headings within content
                item_type_str = f"ast_heading_h{node.get('level', 0)}"
                if node.get('children') and node['children'][0].get('type') == 'text':
                    component_name_for_item = node['children'][0].get('text','').strip()
            elif node_type == 'block_code':
                item_type_str = "code_block"
                raw_node_content = node.get('text', '') # Mistune v3 uses 'text' for content of block_code
            elif node_type == 'block_quote':
                item_type_str = "blockquote"
            # Add more explicit handling for other node types: strong, emphasis, link, image etc. if needed as separate items.
            # For now, they will be part of the raw_content of their parent (e.g., paragraph).

            # Only create an item if it has some meaningful content or is a structural element like a list
            if raw_node_content.strip() or node_type in ['list', 'list_item']:
                item_data: Dict[str, Any] = {
                    "source_file_path": source_file_path,
                    "parent_item_id": parent_item_id,
                    "order_in_parent": current_order,
                    "item_type": item_type_str,
                    "raw_content": raw_node_content.strip(),
                    "extracted_references": self._extract_references_from_text(raw_node_content),
                    "structured_data": [node] # Store the node itself as structured_data for this item
                }
                if component_name_for_item:
                    item_data["component_name"] = component_name_for_item

                item = SFTContentItem(**item_data)
                created_items.append(item)
                current_order += 1

                # Recursively process children for types that have them (list, list_item, block_quote, paragraph for inlines)
                if 'children' in node and isinstance(node['children'], list):
                    # For lists, children are list_items. For list_items, children are blocks (often paragraphs).
                    # For paragraphs, children are inline elements (text, strong, em, link, etc.).
                    # We decide here if we want to create SFTContentItems for these inline elements or just keep them in the paragraph's AST.
                    # For now, let's recurse for list items within lists, and blocks within list_items/blockquotes.
                    # Paragraph children (inlines) will be part of the paragraph's raw_content and its own AST.
                    
                    # Special handling for list_item: its children can be blocks (like paragraphs for its text)
                    # OR a nested list. We want to create SFTContentItems for the nested list separately.
                    children_to_recurse = []
                    if node_type == 'list_item':
                        # For a list_item, its 'children' in AST are the blocks that make up its content.
                        # e.g., [paragraph_node_for_text, nested_list_node]
                        # We only want to recurse for the nested_list_node here to create child SFT items for it.
                        # The paragraph_node_for_text was already handled by _render_node_to_markdown for the list_item's raw_content.
                        for child_node in node.get('children', []):
                            if child_node.get('type') == 'list': # If a child is a nested list
                                children_to_recurse.append(child_node)
                    elif node_type in ['list', 'block_quote']: # For list (children are list_items) or block_quote
                        children_to_recurse = node.get('children', [])

                    if children_to_recurse:
                        child_items, _ = self._create_items_from_ast(
                            children_to_recurse, 
                            item.item_id, 
                            source_file_path,
                            0 
                        )
                        created_items.extend(child_items)
        
        return created_items, current_order

    def parse_file(self, file_path: Path) -> List[SFTContentItem]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

        content_items: List[SFTContentItem] = []
        parsed_meta = self._parse_metadata_block(content)
        
        file_item_data: Dict[str, Any] = {
            "source_file_path": str(file_path.relative_to(self.sft_root_dir)),
            "raw_content": content, 
            "item_type": "document"
        }
        if parsed_meta:
            file_item_data.update({k:v for k,v in parsed_meta.items() if v is not None and k not in file_item_data})
            if "component" in parsed_meta: file_item_data["component_name"] = parsed_meta["component"]
            # Ensure 'references' from metadata is handled correctly if it's a string vs list
            if "references" in parsed_meta and not isinstance(parsed_meta["references"], list):
                parsed_meta["references"] = [str(parsed_meta["references"])]


        metadata_references = []
        if parsed_meta and "references" in parsed_meta:
            meta_refs = parsed_meta.get("references", []) # Should be a list now due to above
            if isinstance(meta_refs, list): metadata_references.extend(str(ref) for ref in meta_refs)
            # No need for elif meta_refs here as it's handled above

        content_references = self._extract_references_from_text(content)
        file_item_data["extracted_references"] = list(set(metadata_references + content_references))
        
        document_item = SFTContentItem(**file_item_data)
        content_items.append(document_item)

        lines = content.splitlines()
        doc_child_order_counter = 0
        
        preamble_lines = []
        first_heading_line_index = -1
        for i, line_content in enumerate(lines):
            if self.heading_regex.match(line_content):
                first_heading_line_index = i
                break
            preamble_lines.append(line_content)

        if preamble_lines:
            preamble_text = "\n".join(preamble_lines).strip()
            if preamble_text:
                preamble_ast = self.markdown_parser(preamble_text)
                preamble_item = SFTContentItem(
                    source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                    item_type="preamble",
                    raw_content=preamble_text, # Keep full preamble markdown here
                    parent_item_id=document_item.item_id,
                    order_in_parent=doc_child_order_counter,
                    extracted_references=self._extract_references_from_text(preamble_text),
                    structured_data=preamble_ast 
                )
                content_items.append(preamble_item)
                ast_children, _ = self._create_items_from_ast(preamble_ast, preamble_item.item_id, preamble_item.source_file_path, 0)
                content_items.extend(ast_children)
                doc_child_order_counter += 1
        
        document_item.raw_content = "" 

        lines_for_sections = lines[first_heading_line_index:] if first_heading_line_index != -1 else []
        
        active_section_item: Optional[SFTContentItem] = None
        current_section_prose_lines: List[str] = []
        section_child_order_counter = 0 

        in_ai_context_block = False
        current_ai_context_name: Optional[str] = None
        current_ai_context_lines: List[str] = []

        for line in lines_for_sections:
            heading_match = self.heading_regex.match(line)
            context_start_match = self.ai_context_start_regex.match(line)
            context_end_match = self.ai_context_end_regex.match(line)

            if heading_match:
                if active_section_item and current_section_prose_lines:
                    prose_text = "\n".join(current_section_prose_lines).strip()
                    if prose_text:
                        print(f"DEBUG SFTParser.parse_file: Processing prose_text for section '{active_section_item.component_name if active_section_item else 'UnknownSection'}', parent_item_id='{active_section_item.item_id}':\n---\n{prose_text[:500]}...\n---") # Debug
                        prose_ast = self.markdown_parser(prose_text)
                        print(f"DEBUG SFTParser.parse_file: Generated prose_ast (len: {len(prose_ast)}). First 2 nodes: {prose_ast[:2] if prose_ast else 'Empty AST'}") # Debug
                        prose_item = SFTContentItem(
                            source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                            item_type="prose_block",
                            raw_content=prose_text,
                            parent_item_id=active_section_item.item_id, 
                            order_in_parent=section_child_order_counter,
                            extracted_references=self._extract_references_from_text(prose_text),
                            structured_data=prose_ast
                        )
                        content_items.append(prose_item)
                        ast_children, _ = self._create_items_from_ast(prose_ast, prose_item.item_id, prose_item.source_file_path, 0)
                        content_items.extend(ast_children)
                        section_child_order_counter += 1
                current_section_prose_lines = []

                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                active_section_item = SFTContentItem(
                    source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                    item_type=f"section_h{level}",
                    component_name=title, 
                    raw_content=title, 
                    parent_item_id=document_item.item_id,
                    order_in_parent=doc_child_order_counter,
                    extracted_references=self._extract_references_from_text(title) 
                )
                content_items.append(active_section_item)
                doc_child_order_counter += 1
                section_child_order_counter = 0 
                in_ai_context_block = False 
            
            elif context_start_match and not in_ai_context_block:
                if active_section_item and current_section_prose_lines: 
                    prose_text = "\n".join(current_section_prose_lines).strip()
                    if prose_text: 
                        prose_ast = self.markdown_parser(prose_text)
                        prose_item = SFTContentItem(
                            source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                            item_type="prose_block",
                            raw_content=prose_text,
                            parent_item_id=active_section_item.item_id,
                            order_in_parent=section_child_order_counter,
                            extracted_references=self._extract_references_from_text(prose_text),
                            structured_data=prose_ast
                        )
                        content_items.append(prose_item)
                        ast_children, _ = self._create_items_from_ast(prose_ast, prose_item.item_id, prose_item.source_file_path, 0)
                        content_items.extend(ast_children)
                        section_child_order_counter += 1
                current_section_prose_lines = [] 

                in_ai_context_block = True
                current_ai_context_name = context_start_match.group(1).strip()
                current_ai_context_lines = []
            
            elif context_end_match and in_ai_context_block:
                parent_id_for_context = active_section_item.item_id if active_section_item else document_item.item_id
                context_block_text = "\n".join(current_ai_context_lines).strip()
                if context_block_text: 
                    context_ast = self.markdown_parser(context_block_text)
                    context_item = SFTContentItem(
                        source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                        item_type="ai_context_block",
                        context_name=current_ai_context_name,
                        raw_content=context_block_text,
                        parent_item_id=parent_id_for_context,
                        order_in_parent=section_child_order_counter,
                        extracted_references=self._extract_references_from_text(context_block_text),
                        structured_data=context_ast
                    )
                    content_items.append(context_item)
                    ast_children, _ = self._create_items_from_ast(context_ast, context_item.item_id, context_item.source_file_path, 0)
                    content_items.extend(ast_children)
                    section_child_order_counter += 1
                
                in_ai_context_block = False
                current_ai_context_name = None
                current_ai_context_lines = []

            elif in_ai_context_block:
                current_ai_context_lines.append(line)
            
            elif active_section_item: 
                current_section_prose_lines.append(line)
            
        if active_section_item and current_section_prose_lines: 
            prose_text = "\n".join(current_section_prose_lines).strip()
            if prose_text:
                prose_ast = self.markdown_parser(prose_text)
                prose_item = SFTContentItem(
                    source_file_path=str(file_path.relative_to(self.sft_root_dir)),
                    item_type="prose_block",
                    raw_content=prose_text,
                    parent_item_id=active_section_item.item_id,
                    order_in_parent=section_child_order_counter,
                    extracted_references=self._extract_references_from_text(prose_text),
                    structured_data=prose_ast
                )
                content_items.append(prose_item)
                ast_children, _ = self._create_items_from_ast(prose_ast, prose_item.item_id, prose_item.source_file_path, 0)
                content_items.extend(ast_children)

        return content_items

    def parse_all_documents(self) -> List[SFTContentItem]:
        all_content_items = []
        markdown_files = self._discover_markdown_files()
        for md_file in markdown_files:
            print(f"Parsing: {md_file.relative_to(self.sft_root_dir)}")
            file_items = self.parse_file(md_file)
            all_content_items.extend(file_items)
        
        print(f"Total files parsed: {len(markdown_files)}")
        print(f"Total content items extracted: {len(all_content_items)}")
        return all_content_items

# Example Usage (conceptual):
# if __name__ == "__main__":
#     sft_repo_root = Path(__file__).resolve().parent.parent.parent 
#     parser = SFTParser(sft_root_dir=str(sft_repo_root))
#     all_items = parser.parse_all_documents()
    
#     for item in all_items:
#         print(f"--- Item ID: {item.item_id}, Type: {item.item_type}, Parent: {item.parent_item_id}, Order: {item.order_in_parent} ---")
#         if hasattr(item, 'component_name') and item.component_name: print(f"  Component: {item.component_name}")
#         if hasattr(item, 'context_name') and item.context_name: print(f"  Context: {item.context_name}")
#         # print(f"  Raw Content Snippet: {item.raw_content[:100]}...")
#         if item.extracted_references: print(f"  References: {item.extracted_references}")
#         if hasattr(item, 'parsed_metadata') and item.parsed_metadata: print(f"  Metadata: {item.parsed_metadata}")
#         if hasattr(item, 'structured_data') and item.structured_data : print(f"  Structured Data (AST snippet): {str(item.structured_data)[:200]}...")
