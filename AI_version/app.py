from datetime import datetime
import uuid
from pathlib import Path

from .sft_parser.parser import SFTParser
from .state_manager.state_manager import StateManager
from .core_models.client import Client, SexEnum
from .core_models.goal import Goal, EntryFrameworkModel
from .logic_engine.decision_engine import (
    DecisionLogicEngine, 
    WORKOUT_IMPLEMENTATION_FILE  # Import the constant
)
from .llm_integration.llm_service import LLMService

def main():
    print("SFT AI Framework - Advanced LLM Integration Test")
    
    # Initialize core components
    sft_documents_root = Path(__file__).resolve().parent.parent
    parser = SFTParser(sft_root_dir=str(sft_documents_root))
    all_items = parser.parse_all_documents()
    state_manager = StateManager()
    state_manager.load_sft_items(all_items)
    llm_service = LLMService()  # Using mock LLM service
    decision_engine = DecisionLogicEngine(state_manager, llm_service)

    print("\n--- Communication Mode Test ---")
    test_cases = [
        ("I'm feeling a lot of anger and frustration lately.", None),
        ("I keep making excuses and need discipline.", None),
        ("Tell me about the strategy for my next phase.", None),
        ("Hello, how are you today?", None),
        ("I want to understand the strategy for Level 1.", "curious"),
        ("I'm procrastinating on my workout again.", None)
    ]

    for text, emotional_state in test_cases:
        mode = decision_engine.recommend_communication_mode(
            client_input_text=text,
            client_emotional_state=emotional_state
        )
        print(f"\nInput: '{text}'")
        if emotional_state:
            print(f"Emotional State: '{emotional_state}'")
        print(f"Recommended Mode: {mode}")
        
        # For procrastination case, also test coaching prompt
        if "procrastinating" in text:
            analysis = llm_service.analyze_client_utterance(text)
            prompt = decision_engine.generate_coaching_prompt(analysis, mode)
            print(f"Coaching Prompt: {prompt}")

    print("\n--- Content Personalization Test ---")
    
    # Create test client
    test_client = Client(
        client_id="test123",
        full_name="Jane Smith",
        age=28,
        sex=SexEnum.FEMALE,
        location="San Francisco, USA",
        height_cm=165.0,
        weight_kg=60.0,
        assessment_data={
            "Primal patterns": True,
            "Ground movement": True,
            "Energy baselines": True,
            "Neural foundations": True
        }
    )
    state_manager.add_client(test_client)

    # Add a test goal
    test_goal = Goal(
        goal_id=str(uuid.uuid4()),
        client_id=test_client.client_id,
        overall_goal_summary="Build strength and mobility",
        entry_framework=EntryFrameworkModel(
            goal_definition="Master basic movement patterns",
            sensory_description="Feel strong and capable",
            purpose_identification="Build a foundation for advanced training"
        )
    )
    state_manager.add_goal(test_goal)
    
    # Find a workout-related content item to personalize
    workout_items = state_manager.get_sft_items(
        source_file_path=WORKOUT_IMPLEMENTATION_FILE,
        item_type="paragraph"
    )
    
    if workout_items:
        sample_item = workout_items[0]
        print(f"\nOriginal Content:")
        print(f"Type: {sample_item.item_type}")
        print(f"Content: {sample_item.raw_content[:100]}...")

        # Create mock client analysis
        mock_analysis = {
            "timestamp": str(datetime.now()),
            "themes": ["motivation", "technique focus"],
            "nuanced_emotion": "determined but uncertain",
            "key_concerns": ["proper form", "progression pace"]
        }

        # Test personalization
        context_tags = ["beginner", "strength focus", "form emphasis"]
        personalized_item = decision_engine.personalize_sft_item(
            client=test_client,
            sft_item_id=sample_item.item_id,
            client_analysis=mock_analysis,
            context_tags=context_tags
        )

        if personalized_item:
            print(f"\nPersonalized Content:")
            print(f"ID: {personalized_item.item_id}")
            print(f"Content: {personalized_item.raw_content}")
            print(f"Metadata: {personalized_item.parsed_metadata}")
        else:
            print("Failed to personalize content")

    print("\nSFT AI Framework - Test Run Complete.")

if __name__ == "__main__":
    main()
