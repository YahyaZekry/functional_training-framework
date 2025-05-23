from typing import Dict, Optional, Any, List

from ..state_manager.state_manager import StateManager
from ..core_models.client import Client
from ..core_models.goal import Goal
from ..core_models.sft_content_item import SFTContentItem
from ..llm_integration.llm_service import LLMService, Sentiment 

COMMUNICATION_MODE_DEFAULT = "DEFAULT_MODE"
COMMUNICATION_MODE_WARRIOR = "WARRIOR_MODE"
COMMUNICATION_MODE_DARKKNIGHT = "DARKKNIGHT_MODE"
COMMUNICATION_MODES = [COMMUNICATION_MODE_DEFAULT, COMMUNICATION_MODE_WARRIOR, COMMUNICATION_MODE_DARKKNIGHT]

EMOTIONAL_TARGETING_FILE = "01-core/07-emotional-targeting.md"
WORKOUT_TEMPLATES_FILE = "04-protocols/programs/01-workout-templates.md"
WORKOUT_IMPLEMENTATION_FILE = "03-systems/training/01-workout-system.md"

class DecisionLogicEngine:
    def __init__(self, state_manager: StateManager, llm_service: LLMService):
        self.state_manager = state_manager
        if not isinstance(state_manager, StateManager):
            raise TypeError("DecisionLogicEngine requires a valid StateManager instance.")
        self.llm_service = llm_service
        if not isinstance(llm_service, LLMService):
            raise TypeError("DecisionLogicEngine requires a valid LLMService instance.")
        self._emotional_targeting_rules: Dict[str, Any] = {}
        self._load_emotional_targeting_rules()

    def determine_sft_level(self, client: Client) -> int:
        """
        Determines client's SFT level based on assessment data.
        Returns level 0-3 based on the criteria met.
        """
        assessment_data = client.assessment_data if client.assessment_data else {}
        
        # Check for self-assessed level first
        self_assessed_level = assessment_data.get("initial_SFT_level_self_assessed")
        if isinstance(self_assessed_level, int) and 0 <= self_assessed_level <= 3:
            return self_assessed_level
            
        # Otherwise evaluate based on criteria
        level_criteria = {
            0: ["Primal patterns", "Ground movement", "Basic locomotion", 
                "Energy baselines", "Neural foundations", "Recovery understanding", 
                "Environmental awareness"],
            1: ["Complex patterns", "Strength progression", "Energy enhancement",
                "Neural adaptation", "Recovery optimization", "Pattern stability",
                "Environmental competence"],
            2: ["Advanced integration", "Power development", "Energy mastery",
                "Neural mastery", "Recovery mastery", "Pattern mastery",
                "Environmental mastery"],
            3: ["Movement innovation", "Strength innovation", "Energy innovation",
                "Neural innovation", "Recovery innovation", "Pattern innovation",
                "Environmental innovation"]
        }

        current_level = 0
        for level_to_check in sorted(level_criteria.keys()):
            criteria = level_criteria[level_to_check]
            if not criteria:
                continue
                
            criteria_met = sum(1 for crit in criteria if assessment_data.get(crit, False))
            threshold = len(criteria) * 0.75  # 75% of criteria must be met
            
            if criteria_met >= threshold:
                current_level = level_to_check
            else:
                break
                
        return current_level

    def _load_emotional_targeting_rules(self):
        """Loads emotional targeting rules from the SFT content."""
        self._emotional_targeting_rules = {
            "triggers": {mode: [] for mode in COMMUNICATION_MODES},
            "state_mapping": {}
        }

        for mode_name, mode_constant_val in [
            ("Default Mode", COMMUNICATION_MODE_DEFAULT),
            ("DarkKnight Mode", COMMUNICATION_MODE_DARKKNIGHT),
            ("Warrior Mode", COMMUNICATION_MODE_WARRIOR)
        ]:
            mode_sections = self.state_manager.get_sft_items(
                component_name=mode_name,
                item_type="section_h3",
                source_file_path=EMOTIONAL_TARGETING_FILE
            )
            if mode_sections:
                mode_section = mode_sections[0]
                prose_blocks = self.state_manager.get_children_of_item(mode_section.item_id)
                if prose_blocks and prose_blocks[0].item_type == "prose_block":
                    ast_items = self.state_manager.get_children_of_item(prose_blocks[0].item_id)
                    for item in ast_items:
                        if item.item_type == "list_block":
                            list_items = self.state_manager.get_children_of_item(item.item_id)
                            for li in list_items:
                                if li.item_type == "list_item" and li.raw_content:
                                    content = li.raw_content.lower().strip()
                                    if content.startswith('[') or not content:
                                        continue
                                    if ":" in content:
                                        state_part, desc_part = content.split(":", 1)
                                        state_part = state_part.strip()
                                        desc_part = desc_part.strip()
                                        if any(skip in state_part for skip in ["prefix", "tone", "structure", "content"]):
                                            continue
                                        self._emotional_targeting_rules["state_mapping"][state_part] = mode_constant_val
                                        desc_words = desc_part.replace("and", ",").replace("-", ",").split(",")
                                        keywords = []
                                        for word in desc_words:
                                            word = word.strip()
                                            if not word or any(skip in word for skip in ["based", "focused"]):
                                                continue
                                            if "motiv" in word: keywords.extend(["motivated", "motivation"])
                                            elif "determin" in word: keywords.extend(["determined", "determination"])
                                            elif "disciplin" in word: keywords.extend(["discipline", "disciplined"])
                                            elif "frustrat" in word: keywords.extend(["frustrated", "frustration"])
                                            elif "struggle" in word: keywords.extend(["struggle", "struggling"])
                                            elif "procrast" in word: keywords.extend(["procrastinate", "procrastinating", "procrastination"])
                                            else: keywords.append(word)
                                        for keyword in set(keywords):
                                            self._emotional_targeting_rules["state_mapping"][keyword] = mode_constant_val
                                    else:
                                        self._emotional_targeting_rules["state_mapping"][content] = mode_constant_val

        # Load trigger phrases for each mode
        trigger_sections = self.state_manager.get_sft_items(
            component_name="Trigger Recognition",
            item_type="section_h3",
            source_file_path=EMOTIONAL_TARGETING_FILE
        )
        if trigger_sections:
            trigger_section = trigger_sections[0]
            prose_blocks = self.state_manager.get_children_of_item(trigger_section.item_id)
            if prose_blocks and prose_blocks[0].item_type == "prose_block":
                ast_items = self.state_manager.get_children_of_item(prose_blocks[0].item_id)
                current_mode = None
                for item in ast_items:
                    if item.item_type == "paragraph":
                        title = item.raw_content.strip()
                        if "DarkKnight Mode Triggers:" in title: current_mode = COMMUNICATION_MODE_DARKKNIGHT
                        elif "Warrior Mode Triggers:" in title: current_mode = COMMUNICATION_MODE_WARRIOR
                        elif "Default Mode Triggers:" in title: current_mode = COMMUNICATION_MODE_DEFAULT
                    elif item.item_type == "list_block" and current_mode:
                        list_items = self.state_manager.get_children_of_item(item.item_id)
                        for li in list_items:
                            if li.item_type == "list_item" and li.raw_content:
                                self._emotional_targeting_rules["triggers"][current_mode].append(li.raw_content.lower())

    def recommend_communication_mode(self, client_input_text: str, 
                                  client_emotional_state: Optional[str] = None) -> str:
        # Perform utterance analysis if LLM service is available
        utterance_analysis: Optional[Dict[str, Any]] = None
        if self.llm_service and client_input_text:
            utterance_analysis = self.llm_service.analyze_client_utterance(client_input_text)

        # Prioritize explicit emotional state if provided
        if client_emotional_state:
            state_lower = client_emotional_state.lower()
            mapped_mode = self._emotional_targeting_rules.get("state_mapping", {}).get(state_lower)
            if mapped_mode:
                return mapped_mode

        text_lower = client_input_text.lower()

        # Check high-priority text triggers (DarkKnight & Warrior)
        mode_trigger_rules = {
            COMMUNICATION_MODE_DARKKNIGHT: [
                ['anger', 'frustration'], ['depression', 'darkness'],
                ['cynical', 'hopeless'], ['struggle', 'pain']
            ],
            COMMUNICATION_MODE_WARRIOR: [
                ['excuses', 'discipline'], ['motivation', 'driven'],
                ['consistency', 'discipline'], ['fear', 'confidence']
            ]
        }

        for mode_to_check in [COMMUNICATION_MODE_DARKKNIGHT, COMMUNICATION_MODE_WARRIOR]:
            # Check loaded emotional triggers from file
            triggers_for_mode = self._emotional_targeting_rules.get("triggers", {}).get(mode_to_check, [])
            for trigger_phrase in triggers_for_mode:
                if trigger_phrase in text_lower:
                    return mode_to_check

            # Check hardcoded keyword combinations
            rules_for_mode = mode_trigger_rules.get(mode_to_check, [])
            for keyword_pair in rules_for_mode:
                if all(word in text_lower for word in keyword_pair):
                    return mode_to_check

        # Check for strategy/learning focused content (DEFAULT priority)
        if any(word in text_lower for word in ["strategy", "how", "what", "when", "understand", "learn", "explain"]):
            return COMMUNICATION_MODE_DEFAULT

        # Check for casual greetings (DEFAULT)
        if len(text_lower.split()) <= 5 and all(word in ["hello", "hi", "hey", "good", "morning", "afternoon", "evening", "how", "are", "you", "today", "thanks", "thank"] for word in text_lower.split()):
            return COMMUNICATION_MODE_DEFAULT

        # Check for emotional content
        emotional_words = ["feel", "feeling", "felt", "want", "need", "must", "should", "struggle", "trying", "hope", "can't", "cant", "procrastinating", "overwhelmed", "frustrated"]
        if any(word in text_lower for word in emotional_words):
            # If we have utterance analysis, use it to determine the mode
            if utterance_analysis and utterance_analysis.get("nuanced_emotion"):
                nuanced_emotion = utterance_analysis["nuanced_emotion"].lower()
                # Map nuanced emotion to mode using emotional targeting rules
                for state_key, mode_val in self._emotional_targeting_rules.get("state_mapping", {}).items():
                    if any(word in nuanced_emotion for word in state_key.split()):
                        return mode_val
            # Default to DARKKNIGHT for unclassified emotional content
            return COMMUNICATION_MODE_DARKKNIGHT

        # Fallback to DEFAULT_MODE
        return COMMUNICATION_MODE_DEFAULT

    def generate_coaching_prompt(self, client_analysis: Dict[str, Any], current_mode: str) -> str:
        """
        Generates a relevant coaching prompt based on client analysis and current mode.
        """
        prompt_text = f"Client utterance analysis: {client_analysis}. Current SFT Mode: {current_mode}."

        if self.llm_service:
            generated_prompt = self.llm_service.generate_chat_response(
                prompt_text=prompt_text,
                sft_mode=current_mode
            )
            if generated_prompt and generated_prompt.startswith(f"[{current_mode}]: "):
                generated_prompt = generated_prompt.replace(f"[{current_mode}]: ", "", 1)
            return f"(Mock LLM Suggestion for {current_mode}): {generated_prompt}"

        # Fallback mock responses
        if current_mode == COMMUNICATION_MODE_WARRIOR:
            if "procrastination" in client_analysis.get("themes", []):
                return "What's one small action you can take RIGHT NOW to overcome this procrastination?"
            return "What's your next move, warrior? How will you conquer this challenge?"
        elif current_mode == COMMUNICATION_MODE_DARKKNIGHT:
            if "struggle" in client_analysis.get("themes", []):
                return "Acknowledge the struggle. What strength can you forge from this darkness?"
            return "The path through darkness requires unyielding focus. What must be done?"
        else:  # DEFAULT_MODE
            if "goal clarity" in client_analysis.get("themes", []):
                return "It sounds like clarifying your goal could be helpful. What would success look like for you?"
            return "Interesting. Could you tell me more about that?"

    def personalize_sft_item(self, client: Client, sft_item_id: str, 
                          client_analysis: Optional[Dict[str, Any]] = None, 
                          context_tags: Optional[List[str]] = None) -> Optional[SFTContentItem]:
        """
        Personalizes an SFTContentItem for a given client based on their data,
        recent utterance analysis, and contextual tags.
        Returns a *new* SFTContentItem instance with personalized content,
        or None if the original item is not found.
        """
        original_item = self.state_manager.get_sft_item_by_id(sft_item_id)
        if not original_item:
            return None

        # Create new item with unique ID for personalized version
        personalized_item = SFTContentItem(
            item_id=f"{original_item.item_id}_personalized_{client.client_id[:8]}",
            item_type=original_item.item_type,
            raw_content=original_item.raw_content, 
            source_file_path=original_item.source_file_path,
            parent_item_id=original_item.parent_item_id,
            order_in_parent=original_item.order_in_parent,
            component_name=original_item.component_name,
            context_name=original_item.context_name,
            parsed_metadata=original_item.parsed_metadata.copy() if original_item.parsed_metadata else {},
        )

        # Add personalization metadata
        personalized_item.parsed_metadata["personalized_for_client"] = client.client_id
        if client_analysis:
            personalized_item.parsed_metadata["personalization_timestamp"] = client_analysis.get("timestamp", "N/A")
        else:
            personalized_item.parsed_metadata["personalization_timestamp"] = "N/A"

        # Build personalization details summary
        personalization_details = (
            f"\n--- Personalized for {client.full_name} "
            f"(Level {self.determine_sft_level(client)}) ---\n"
        )
        if client_analysis:
            themes = client_analysis.get('themes', [])
            nuanced_emotion = client_analysis.get('nuanced_emotion', 'N/A')
            if themes:
                personalization_details += f"Based on themes: {', '.join(themes)}.\n"
            if nuanced_emotion != 'N/A':
                personalization_details += f"Current emotional state: {nuanced_emotion}.\n"
        if context_tags:
            personalization_details += f"Context tags: {', '.join(context_tags)}.\n"

        if self.llm_service:
            # Get client's active goals for context
            client_goals = self.state_manager.get_active_goals_by_client_id(client.client_id)
            goals_summary = ", ".join([goal.overall_goal_summary for goal in client_goals]) if client_goals else "Not specified"

            # Build analysis summary for LLM prompt
            recent_analysis_summary = "Not available"
            if client_analysis:
                themes = client_analysis.get('themes', [])
                nuanced_emotion = client_analysis.get('nuanced_emotion')
                parts = []
                if themes:
                    parts.append(f"Themes: {', '.join(themes)}")
                if nuanced_emotion:
                    parts.append(f"Emotion: {nuanced_emotion}")
                if parts:
                    recent_analysis_summary = "; ".join(parts)

            # Prepare LLM prompt for personalization
            context_tags_summary = ', '.join(context_tags) if context_tags else 'None'
            prompt_for_personalization = (
                f"Original content: \"{original_item.raw_content[:200]}...\"\n"
                f"Client profile: Age {client.age}, Level {self.determine_sft_level(client)}, Goals: {goals_summary}\n"
                f"Recent client analysis: {recent_analysis_summary}\n"
                f"Context tags: {context_tags_summary}\n"
                f"Task: Personalize this content considering the client's level, goals, and emotional state. "
                f"Make it relevant and engaging while preserving the core message."
            )

            # Get personalized content suggestion from LLM
            personalized_content = "(No personalized content generated)"
            llm_response = self.llm_service.generate_chat_response(
                prompt_text=prompt_for_personalization,
                sft_mode=COMMUNICATION_MODE_DEFAULT
            )
            if llm_response:
                if llm_response.startswith(f"[{COMMUNICATION_MODE_DEFAULT}]: "):
                    personalized_content = llm_response.replace(f"[{COMMUNICATION_MODE_DEFAULT}]: ", "", 1)
                else:
                    personalized_content = llm_response

            personalized_item.raw_content = (
                f"{personalized_content}\n"
                f"Original snippet: {original_item.raw_content[:50]}...\n"
                f"{personalization_details}"
            )
        else:
            # Mock personalization if no LLM service
            personalized_item.raw_content = (
                f"(Mock Personalized Content for {client.full_name}): "
                f"This content has been adapted for you! "
                f"Original: {original_item.raw_content[:50]}...\n"
                f"{personalization_details}"
            )

        return personalized_item
