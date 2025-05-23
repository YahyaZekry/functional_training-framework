from typing import Dict, List, Optional, Any, Literal

# Define possible sentiment values
Sentiment = Literal["positive", "negative", "neutral", "mixed"]

# Define a type for conversation history messages
ChatMessage = Dict[str, str] # e.g., {"role": "user", "content": "Hello"} or {"role": "assistant", "content": "Hi there!"}

class LLMService:
    """
    Abstract base class or primary interface for Large Language Model services.
    Concrete implementations will interface with specific LLM providers (e.g., OpenAI, Anthropic).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name
        if self.api_key:
            print(f"LLMService: Initialized with API key (type: {type(self).__name__}). Model: {self.model_name or 'default'}")
        else:
            print(f"LLMService: Initialized in mock mode (type: {type(self).__name__}). Model: {self.model_name or 'mock_default'}")

    def analyze_sentiment(self, text: str) -> Sentiment:
        """
        Analyzes the sentiment of the given text.
        Returns one of "positive", "negative", "neutral", "mixed".
        Mock implementation.
        """
        print(f"LLMService (mock): Analyzing sentiment for text: '{text[:50]}...'")
        if "sad" in text.lower() or "angry" in text.lower() or "frustration" in text.lower():
            return "negative"
        if "happy" in text.lower() or "great" in text.lower() or "excited" in text.lower():
            return "positive"
        if "but" in text.lower() or "however" in text.lower():
            return "mixed"
        return "neutral"

    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Extracts named entities from the text.
        entity_types can be used to specify which types to look for (e.g., ["date", "exercise_name"]).
        Returns a dictionary where keys are entity types and values are lists of extracted entities.
        Mock implementation.
        """
        print(f"LLMService (mock): Extracting entities for text: '{text[:50]}...' (types: {entity_types})")
        entities: Dict[str, List[str]] = {}
        if "push ups" in text.lower():
            entities.setdefault("exercise_name", []).append("Push Ups")
        if "next monday" in text.lower():
            entities.setdefault("date", []).append("next monday")
        if not entities:
            entities["unknown"] = ["mock_entity"]
        return entities

    def generate_chat_response(self, 
                               prompt_text: str, 
                               sft_mode: str, # e.g., "DEFAULT_MODE", "WARRIOR_MODE"
                               conversation_history: Optional[List[ChatMessage]] = None
                               ) -> str:
        """
        Generates a chat response based on the prompt, SFT mode, and conversation history.
        The SFT mode should guide the tone and style of the response.
        Mock implementation.
        """
        print(f"LLMService (mock): Generating chat response for prompt: '{prompt_text[:50]}...', SFT Mode: {sft_mode}")
        
        prefix = f"[{sft_mode}]: "
        
        if sft_mode == "WARRIOR_MODE":
            response = "GET IT DONE! NO EXCUSES! That's a mock response, by the way. STAY HARD!"
        elif sft_mode == "DARKKNIGHT_MODE":
            response = "Darkness. Pain. This is the path. (This is a mock response from the shadows.)"
        elif sft_mode == "DEFAULT_MODE":
            response = "Understood. Based on your input, a logical next step would be... (mock response)."
        else: # Fallback for unknown modes
            response = f"Processing your request in {sft_mode}... (mock response)."
            prefix = "" # No prefix if mode is unknown

        return prefix + response

    def analyze_client_utterance(self, text: str) -> Dict[str, Any]:
        """
        Performs a deeper analysis of the client's utterance.
        Returns a dictionary with keys like "themes", "nuanced_emotion", "obstacles", "opportunities".
        Mock implementation.
        """
        print(f"LLMService (mock): Analyzing client utterance: '{text[:50]}...'")
        analysis: Dict[str, Any] = {
            "themes": ["mock_theme_1", "mock_theme_2"],
            "nuanced_emotion": "mock_nuanced_emotion (e.g., hopeful but anxious)",
            "obstacles": [],
            "opportunities": ["mock_coaching_opportunity_1"]
        }
        if "procrastinating" in text.lower() or "can't seem to start" in text.lower():
            analysis["themes"].append("procrastination")
            analysis["obstacles"].append("difficulty initiating tasks")
            analysis["nuanced_emotion"] = "frustrated with self"
            analysis["opportunities"].append("explore underlying reasons for procrastination")
        if "workout" in text.lower() and "hard" in text.lower():
            analysis["themes"].append("workout difficulty")
            analysis["nuanced_emotion"] = "feeling challenged"
        if "goal" in text.lower() and ("clear" in text.lower() or "unsure" in text.lower()):
            analysis["themes"].append("goal clarity")
            analysis["obstacles"].append("unclear objectives")
            analysis["opportunities"].append("goal refinement session")
        
        return analysis

    # Potential future methods:
    # - summarize_text(text: str, length: str = "medium") -> str
    # - translate_text(text: str, target_language: str) -> str
    # - answer_question_from_context(question: str, context: str) -> str

# Example of a concrete implementation (would be in a separate file or conditional import)
# class OpenAILLMService(LLMService):
#     def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
#         super().__init__(api_key, model_name)
#         # Initialize OpenAI client here
#         # from openai import OpenAI
#         # self.client = OpenAI(api_key=self.api_key)
#         print("OpenAILLMService: Initialized with OpenAI client.")

#     def analyze_sentiment(self, text: str) -> Sentiment:
#         # Actual OpenAI API call for sentiment
#         print(f"OpenAILLMService: Analyzing sentiment for '{text[:50]}...' using {self.model_name}")
#         # response = self.client.chat.completions.create(...)
#         # mock_sentiment = super().analyze_sentiment(text) # Call base mock for now
#         # return mock_sentiment
#         return "neutral" # Placeholder

#     def generate_chat_response(self, prompt_text: str, sft_mode: str, conversation_history: Optional[List[ChatMessage]] = None) -> str:
#         # Actual OpenAI API call, potentially with system prompt modified by sft_mode
#         print(f"OpenAILLMService: Generating response for '{prompt_text[:50]}...' in {sft_mode} using {self.model_name}")
#         # system_prompt = f"You are an SFT AI assistant. Respond in {sft_mode}."
#         # messages = [{"role": "system", "content": system_prompt}]
#         # if conversation_history: messages.extend(conversation_history)
#         # messages.append({"role": "user", "content": prompt_text})
#         # response = self.client.chat.completions.create(model=self.model_name, messages=messages)
#         # return response.choices[0].message.content
#         return super().generate_chat_response(prompt_text, sft_mode, conversation_history) # Call base mock for now
