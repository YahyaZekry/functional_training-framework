from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

class SFTContentItem(BaseModel):
    """
    Represents a parsed item of content from the SFT markdown documents.
    This could be a section, a specific protocol, a principle, metadata, etc.
    """
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file_path: str  # Relative path to the .md file
    
    # Extracted from AI.METADATA or inferred
    component_name: Optional[str] = None 
    version: Optional[str] = None
    framework_type: Optional[str] = None # e.g., goal_definition, core_mission
    language: Optional[str] = None
    parent_doc_name: Optional[str] = None # From 'parent' in metadata
    
    item_type: str # e.g., 'document', 'preamble', 'section_h1', 'prose_block', 'paragraph', 'ai_context_block'
    
    tags: List[str] = Field(default_factory=list) # Could be extracted from text or specific tags
    
    raw_content: str # The raw markdown text of this specific item
    
    parsed_metadata: Optional[Dict[str, Any]] = None # Stores the directly parsed key-value pairs from AI.METADATA
    
    # For structured data within the content, if applicable
    # e.g., if a list is parsed into actual list items, or key-value pairs
    structured_data: Optional[List[Dict[str, Any]]] = None # Mistune AST is a list of dicts
    
    # For <!-- AI.CONTEXT: ... --> blocks or similar
    context_name: Optional[str] = None 
    
    # For {ref: ...} tags
    extracted_references: List[str] = Field(default_factory=list) 
    
    # For hierarchical structuring within a document
    parent_item_id: Optional[str] = None # To link to a parent SFTContentItem
    order_in_parent: Optional[int] = None # Sequence of this item under its parent
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # last_parsed_at: Optional[datetime] = None # Could be useful if reparsing

    class Config:
        validate_assignment = True

# Example (conceptual, parser would create these):
# if __name__ == "__main__":
#     metadata_item = SFTContentItem(
#         source_file_path="01-core/05-unified-goal-framework.md",
#         item_type="metadata_block",
#         component_name="unified_goal_framework",
#         version="3.1",
#         framework_type="goal_definition",
#         language="en-US",
#         parent_doc_name="superfunctional_training_system",
#         raw_content="<!-- AI.METADATA ... -->",
#         parsed_metadata={
#             "component": "unified_goal_framework", 
#             "version": "3.1", 
#             # ... other metadata fields
#         }
#     )
#     print(metadata_item.model_dump_json(indent=2))

#     principle_item = SFTContentItem(
#         source_file_path="01-core/05-unified-goal-framework.md",
#         item_type="principle",
#         raw_content="- Specific and measurable",
#         parent_item_id=metadata_item.item_id # Assuming metadata block is parent conceptually
#     )
#     print(principle_item.model_dump_json(indent=2))
