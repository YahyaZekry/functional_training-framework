from typing import Dict, List, Optional, Any
import os
import json

from .llm_service import LLMService, Sentiment, ChatMessage
# We'll need a way to call the MCP tool. For now, this is a placeholder.
# In a real scenario, this might be a helper function or class that encapsulates MCP calls.
# For this implementation, I will assume the MCP call happens directly where needed.

class PerplexityLLMService(LLMService):
    """
    Concrete implementation of LLMService using the Perplexity AI MCP.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = "sonar-medium-chat"):
        # Perplexity API key is usually handled by the MCP server environment,
        # but can be passed for other configurations.
        # Model name can be specified, e.g., "sonar-small-chat", "sonar-medium-chat", "sonar-large-chat"
        # or "sonar-small-online", "sonar-medium-online", "sonar-large-online" for web-connected models.
        super().__init__(api_key, model_name) # api_key might not be directly used if MCP handles it
        print(f"PerplexityLLMService: Initialized. Model: {self.model_name}")
        # We will use the 'github.com/pashpashpash/perplexity-mcp' server
        self.mcp_server_name = "github.com/pashpashpash/perplexity-mcp"

    def _call_perplexity_chat(self, prompt: str, system_prompt: Optional[str] = None, chat_history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """
        Helper method to make a call to the Perplexity chat_perplexity tool.
        This method will be used by other service methods.
        It needs to be adapted to use the actual <use_mcp_tool> structure when used by the AI agent.
        For now, it simulates the expected output structure of the MCP tool.
        """
        # This is a conceptual representation. The actual call will be an MCP tool use.
        # For local testing, one might mock this or directly use a Perplexity client if available.
        print(f"PerplexityLLMService (conceptual): Calling chat_perplexity with prompt: '{prompt[:50]}...'")
        
        # Placeholder: In a real scenario, this would be where the <use_mcp_tool> call is constructed and executed.
        # The response from the MCP tool would then be processed.
        # For now, we'll return a mock success structure.
        
        # Constructing a message for the Perplexity API via MCP
        # The actual prompt to Perplexity might be more complex, combining user prompt, system prompt, and history.
        # For simplicity, we'll use the main prompt for now.
        
        # This is a mock response structure that the actual MCP tool might return or be processed into.
        mock_mcp_response = {
            "success": True,
            "data": {
                "chat_id": "mock_chat_id_123",
                "response": f"Mock Perplexity response to: {prompt}",
                "full_response": { # This structure might vary based on actual MCP tool
                    "choices": [{"message": {"content": f"Mock Perplexity response to: {prompt}"}}]
                }
            }
        }
        # Simulate getting the content
        response_content = mock_mcp_response["data"]["full_response"]["choices"][0]["message"]["content"]
        
        # This is what the methods below will expect to work with.
        return {"content": response_content} # Simplified return for direct use by other methods

    def analyze_sentiment(self, text: str) -> Sentiment:
        print(f"PerplexityLLMService: Analyzing sentiment for text: '{text[:50]}...'")
        system_prompt = "You are a sentiment analysis expert. Classify the following text as 'positive', 'negative', 'neutral', or 'mixed'. Respond with only one of these words."
        # In a real call, this would use the MCP tool:
        # <use_mcp_tool>
        # <server_name>{self.mcp_server_name}</server_name>
        # <tool_name>chat_perplexity</tool_name>
        # <arguments>{{"message": f"{system_prompt}\n\nText: {text}"}}</arguments>
        # </use_mcp_tool>
        # For now, simulate a call and a plausible response processing
        
        # Conceptual call to Perplexity via MCP
        # This is where the <use_mcp_tool> call would be made by the agent.
        # For example:
        # mcp_arguments = {
        #     "message": f"{system_prompt}\n\nText to analyze: \"{text}\"",
        #     "chat_id": None # Or manage chat_id for ongoing sentiment analysis context
        # }
        # # AGENT ACTION: <use_mcp_tool>
        # # <server_name>{self.mcp_server_name}</server_name>
        # # <tool_name>chat_perplexity</tool_name>
        # # <arguments>{json.dumps(mcp_arguments)}</arguments>
        # # </use_mcp_tool>
        # # AGENT RECEIVES: mcp_result = ... (actual result from the tool)

        # This method is now designed to be called by an agent (like me).
        # The agent will perform the actual <use_mcp_tool> call.
        # This method's role is to define the prompt and process the result.

        # Step 1: Define the prompt for the LLM (handled by the agent when making the call)
        # system_prompt = "You are a sentiment analysis expert..."
        # mcp_message = f"{system_prompt}\n\nText to analyze: \"{text}\""
        # (The agent would construct the full arguments for the MCP tool call)

        # Step 2: Agent makes the MCP call (external to this Python code)
        # Example:
        # <use_mcp_tool>
        #  <server_name>github.com/pashpashpash/perplexity-mcp</server_name>
        #  <tool_name>chat_perplexity</tool_name>
        #  <arguments>{"message": mcp_message, "model_name": self.model_name}</arguments>
        # </use_mcp_tool>
        # Agent receives mcp_tool_result (e.g., {"chat_id": "...", "response": "mixed [1]"})

        # Step 3: This method would be called *by the agent* with the mcp_tool_result.
        # For now, to make it runnable by app.py directly for testing the flow,
        # we'll keep a simplified mock logic here.
        # The true test of MCP integration is when the agent uses this method's guidance
        # to make the call and then passes the result back for processing (which isn't fully implemented here yet).
        
        print(f"INFO: PerplexityLLMService.analyze_sentiment - Agent would make MCP call for: '{text[:30]}...'")
        # This simple mock is for when app.py calls this directly.
        text_lower_mock = text.lower()
        if "sad" in text_lower_mock or "angry" in text_lower_mock or "frustration" in text_lower_mock:
            return "negative"
        if "happy" in text_lower_mock or "great" in text_lower_mock or "excited" in text_lower_mock:
            return "positive"
        if "but" in text_lower_mock or "however" in text_lower_mock:
            return "mixed"
        return "neutral"

    def _process_sentiment_mcp_response(self, mcp_response_text: str) -> Sentiment:
        """
        Helper to process the raw text response from the Perplexity MCP
        for sentiment analysis. Extracts the sentiment word.
        Example input: "<think>...</think>\n\nmixed [1][4]"
        """
        # Remove <think> block if present
        if "<think>" in mcp_response_text and "</think>" in mcp_response_text:
            think_end_index = mcp_response_text.find("</think>") + len("</think>")
            processed_text = mcp_response_text[think_end_index:]
        else:
            processed_text = mcp_response_text
        
        # Remove source citations like [1][4]
        import re
        processed_text = re.sub(r'\s*\[\d+\]\s*', '', processed_text).strip()
        
        # Get the first word, which should be the sentiment
        sentiment_candidate = processed_text.split()[0].lower() if processed_text else "neutral"

        if sentiment_candidate in ["positive", "negative", "neutral", "mixed"]:
            return sentiment_candidate # type: ignore
        else:
            print(f"Warning: _process_sentiment_mcp_response received unexpected value: {sentiment_candidate} from '{mcp_response_text}'")
            return "neutral"

    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
        print(f"PerplexityLLMService: Extracting entities for text: '{text[:50]}...' (types: {entity_types})")
        entity_prompt = f"Extract the following entity types: {json.dumps(entity_types) if entity_types else 'all common entities (e.g., dates, locations, names, organizations, exercises)'} from the text below. Respond in JSON format like {{'entity_type': ['value1', 'value2']}}.\n\nText: {text}"
        # Conceptual call to Perplexity via MCP
        # response_data = self._call_perplexity_chat(prompt=entity_prompt)
        # try:
        #     entities = json.loads(response_data.get("content", "{}"))
        # except json.JSONDecodeError:
        #     entities = {"error": "Failed to parse LLM entity response"}
        # return entities

        # Simulate receiving a result from the MCP tool
        # This method guides the agent on how to call the MCP tool for entity extraction.
        # The agent makes the call, then this method (or a helper) processes the result.

        # Step 1: Define the prompt (handled by agent)
        # entity_prompt = f"Extract ... Respond in JSON format ...\n\nText: {text}"

        # Step 2: Agent makes MCP call
        # <use_mcp_tool> ... arguments: {"message": entity_prompt, ...} ... </use_mcp_tool>
        # Agent receives mcp_tool_result (e.g., {"chat_id": "...", "response": "{ \"date\": [\"next monday\"] }"})

        # Step 3: This method (or a helper) processes mcp_tool_result.
        # For app.py direct calls, use simple mock:
        print(f"INFO: PerplexityLLMService.extract_entities - Agent would make MCP call for: '{text[:30]}...'")
        mock_entities_data: Dict[str, List[str]] = {}
        text_lower_mock = text.lower()
        if "push ups" in text_lower_mock: 
            mock_entities_data.setdefault("exercise_name", []).append("Push Ups")
        if "next monday" in text_lower_mock: 
            mock_entities_data.setdefault("date", []).append("next monday")
        
        if not mock_entities_data and entity_types:
            mock_entities_data[entity_types[0]] = ["mock_entity_value_px"]
        elif not mock_entities_data:
            mock_entities_data["unknown"] = ["mock_entity_value_px"]
        return mock_entities_data

    def _process_entities_mcp_response(self, mcp_response_text: str) -> Dict[str, List[str]]:
        """
        Helper to process the raw text response from Perplexity MCP for entity extraction.
        Expects the core response to be a JSON string.
        """
        # Remove <think> block if present
        if "<think>" in mcp_response_text and "</think>" in mcp_response_text:
            think_end_index = mcp_response_text.find("</think>") + len("</think>")
            json_candidate_text = mcp_response_text[think_end_index:]
        else:
            json_candidate_text = mcp_response_text
        
        # Remove source citations and clean up
        import re
        json_candidate_text = re.sub(r'\s*\[\d+\]\s*', '', json_candidate_text).strip()
        
        # The LLM might sometimes wrap JSON in ```json ... ```, so try to extract that.
        if json_candidate_text.startswith("```json"):
            json_candidate_text = json_candidate_text[len("```json"):]
            if json_candidate_text.endswith("```"):
                json_candidate_text = json_candidate_text[:-len("```")]
            json_candidate_text = json_candidate_text.strip()

        try:
            entities = json.loads(json_candidate_text)
            if not isinstance(entities, dict):
                raise json.JSONDecodeError("LLM response is not a JSON object.", json_candidate_text, 0)
            for key in entities: # Ensure values are lists of strings
                if not isinstance(entities[key], list):
                    entities[key] = [str(entities[key])]
                else:
                    entities[key] = [str(item) for item in entities[key]]
            return entities
        except json.JSONDecodeError as e:
            print(f"Warning: _process_entities_mcp_response failed to parse LLM JSON: {e} from '{json_candidate_text}'")
            return {"error": [f"Failed to parse LLM entity response: {e.msg}"]}

    def generate_chat_response(self, 
                               prompt_text: str, 
                               sft_mode: str, 
                               conversation_history: Optional[List[ChatMessage]] = None
                               ) -> str:
        print(f"PerplexityLLMService: Generating chat response for prompt: '{prompt_text[:50]}...', SFT Mode: {sft_mode}")
        
        # Construct a system prompt based on SFT mode
        # This is a simplified example; real SFT mode integration would be more nuanced.
        sft_system_prompt = f"You are an SFT AI assistant. Your current communication mode is {sft_mode}. Respond accordingly."
        
        # Conceptual call to Perplexity via MCP, including history and system prompt
        # The actual MCP call would need to structure messages correctly for Perplexity.
        # messages_for_mcp = [{"role": "system", "content": sft_system_prompt}]
        # if conversation_history:
        #     messages_for_mcp.extend(conversation_history)
        # messages_for_mcp.append({"role": "user", "content": prompt_text})
        # mcp_args = {"messages": messages_for_mcp} # This depends on how perplexity-mcp handles history
        # response_data = self._call_perplexity_chat(prompt=prompt_text, system_prompt=sft_system_prompt, chat_history=conversation_history)
        # return response_data.get("content", "Error: Could not generate response.")

        # Simulate receiving a result from the MCP tool
        # AGENT ACTION: <use_mcp_tool> with appropriate arguments for chat_perplexity,
        # including handling of sft_system_prompt and conversation_history.
        # AGENT RECEIVES: mcp_result = ...
        # For now, simulate a text response.
        
        simulated_mcp_response_content = ""
        if sft_mode == "WARRIOR_MODE": 
            simulated_mcp_response_content = f"Perplexity WARRIOR says: Responding to '{prompt_text[:30]}...' GET IT DONE!"
        elif sft_mode == "DARKKNIGHT_MODE": 
            simulated_mcp_response_content = f"Perplexity DARKKNIGHT whispers: Contemplating '{prompt_text[:30]}...' Embrace the challenge."
        else: 
            simulated_mcp_response_content = f"Perplexity DEFAULT says: Processing '{prompt_text[:30]}...'."

        # The MCP tool itself might return the direct text, or a structure from which we extract it.
        # Assuming direct text for this simulation.
        response_text = simulated_mcp_response_content
        
        # The prefix is added here for clarity in testing that PerplexityLLMService was used.
        # In a real application, the DecisionLogicEngine might handle presentation.
        return f"[{sft_mode} via PerplexityLLMService]: {response_text}" # This mock is for app.py direct calls

    def _process_chat_mcp_response(self, mcp_response_text: str) -> str:
        """
        Helper to process the raw text response from Perplexity MCP for chat generation.
        Removes <think> block and citations.
        """
        # Remove <think> block if present
        if "<think>" in mcp_response_text and "</think>" in mcp_response_text:
            think_end_index = mcp_response_text.find("</think>") + len("</think>")
            processed_text = mcp_response_text[think_end_index:]
        else:
            processed_text = mcp_response_text
        
        # Remove source citations like [1][4] and clean up
        import re
        processed_text = re.sub(r'\s*\[\d+\]\s*', '', processed_text).strip()
        return processed_text

    def analyze_client_utterance(self, text: str) -> Dict[str, Any]:
        print(f"PerplexityLLMService: Analyzing client utterance: '{text[:50]}...'")
        analysis_prompt = (
            "Analyze the following client utterance from a coaching context. "
            "Identify key themes, nuanced emotion (e.g., hopeful but anxious, frustrated with self), "
            "potential obstacles or challenges mentioned or implied, and any coaching opportunities. "
            "Respond in JSON format with keys: 'themes' (list of strings), 'nuanced_emotion' (string), "
            "'obstacles' (list of strings), 'opportunities' (list of strings).\n\n"
            f"Client utterance: \"{text}\""
        )
        # Conceptual call to Perplexity via MCP
        # response_data = self._call_perplexity_chat(prompt=analysis_prompt)
        # try:
        #     analysis = json.loads(response_data.get("content", "{}"))
        # except json.JSONDecodeError:
        #     analysis = {"error": "Failed to parse LLM analysis response"}
        # return analysis
        
        # Simulate receiving a result from the MCP tool
        # AGENT ACTION: <use_mcp_tool> for analysis_prompt
        # AGENT RECEIVES: mcp_result = ...
        # For now, simulate a JSON string response.
        simulated_mcp_json_response = "{}"
        text_lower = text.lower() 
        
        mock_data_for_sim: Dict[str, Any] = {
            "themes": ["mock_theme_perplexity_default"],
            "nuanced_emotion": "mock_nuanced_emotion_perplexity_default",
            "obstacles": [],
            "opportunities": ["mock_opportunity_perplexity_default"]
        }

        if "procrastinating" in text_lower:
            mock_data_for_sim["themes"] = ["procrastination_px", "avoidance_px"]
            mock_data_for_sim["nuanced_emotion"] = "frustrated_with_self_px"
            mock_data_for_sim["obstacles"] = ["difficulty_initiating_tasks_px", "lack_of_motivation_px"]
            mock_data_for_sim["opportunities"] = ["explore_underlying_reasons_px", "break_down_tasks_px"]
        elif "hard" in text_lower and "workout" in text_lower:
            mock_data_for_sim["themes"] = ["workout_difficulty_px", "challenge_px"]
            mock_data_for_sim["nuanced_emotion"] = "feeling_challenged_px"
        
        simulated_mcp_json_response = json.dumps(mock_data_for_sim)

        try:
            analysis = json.loads(simulated_mcp_json_response)
            if not isinstance(analysis, dict):
                 raise json.JSONDecodeError("LLM response is not a JSON object.", simulated_mcp_json_response, 0)
            # Basic validation of expected keys (can be expanded)
            expected_keys = ["themes", "nuanced_emotion", "obstacles", "opportunities"]
            for key in expected_keys:
                if key not in analysis:
                    analysis[key] = [] if key in ["themes", "obstacles", "opportunities"] else "N/A" # Provide default
        except json.JSONDecodeError as e:
            print(f"Warning: PerplexityLLMService.analyze_client_utterance failed to parse LLM JSON: {e}")
            analysis = {
                "themes": [], "nuanced_emotion": "error_parsing_llm", 
                "obstacles": [], "opportunities": [],
                "error": f"Failed to parse LLM analysis response: {e.msg}"
            }
        return analysis

    def _process_analysis_mcp_response(self, mcp_response_text: str) -> Dict[str, Any]:
        """
        Helper to process the raw text response from Perplexity MCP for utterance analysis.
        Expects the core response to be a JSON string.
        """
        # Remove <think> block if present
        if "<think>" in mcp_response_text and "</think>" in mcp_response_text:
            think_end_index = mcp_response_text.find("</think>") + len("</think>")
            json_candidate_text = mcp_response_text[think_end_index:]
        else:
            json_candidate_text = mcp_response_text
        
        # Remove source citations and clean up
        import re
        json_candidate_text = re.sub(r'\s*\[\d+\]\s*', '', json_candidate_text).strip()

        # The LLM might sometimes wrap JSON in ```json ... ```, so try to extract that.
        if json_candidate_text.startswith("```json"):
            json_candidate_text = json_candidate_text[len("```json"):]
            if json_candidate_text.endswith("```"):
                json_candidate_text = json_candidate_text[:-len("```")]
            json_candidate_text = json_candidate_text.strip()
        
        try:
            analysis = json.loads(json_candidate_text)
            if not isinstance(analysis, dict):
                 raise json.JSONDecodeError("LLM response is not a JSON object.", json_candidate_text, 0)
            # Basic validation of expected keys
            expected_keys = ["themes", "nuanced_emotion", "obstacles", "opportunities"]
            for key in expected_keys:
                if key not in analysis: # Provide default empty values if keys are missing
                    analysis[key] = [] if key in ["themes", "obstacles", "opportunities"] else "N/A"
            return analysis
        except json.JSONDecodeError as e:
            print(f"Warning: _process_analysis_mcp_response failed to parse LLM JSON: {e} from '{json_candidate_text}'")
            return {
                "themes": [], "nuanced_emotion": "error_parsing_llm", 
                "obstacles": [], "opportunities": [],
                "error": f"Failed to parse LLM analysis response: {e.msg}"
            }

# Example usage (for testing this file directly, not part of the main app flow yet)
if __name__ == '__main__':
    # This assumes PERPLEXITY_API_KEY is set in the environment if needed by a direct client
    # For MCP, the server handles the key.
    # perplexity_service = PerplexityLLMService(api_key=os.getenv("PERPLEXITY_API_KEY"))
    perplexity_service_mock = PerplexityLLMService() # No API key needed for current mock structure

    sample_text = "I'm feeling quite happy about my progress, but a bit sad about the workout I missed."
    
    print(f"\nSentiment Analysis for: '{sample_text}'")
    sentiment = perplexity_service_mock.analyze_sentiment(sample_text)
    print(f"-> Sentiment: {sentiment}")

    print(f"\nEntity Extraction for: '{sample_text} I did push ups next monday.'")
    entities = perplexity_service_mock.extract_entities(sample_text + " I did push ups next monday.", entity_types=["exercise_name", "date"])
    print(f"-> Entities: {entities}")

    print(f"\nChat Response (DEFAULT_MODE) for: 'Hello there'")
    chat_resp_default = perplexity_service_mock.generate_chat_response("Hello there", "DEFAULT_MODE")
    print(f"-> Response: {chat_resp_default}")
    
    print(f"\nChat Response (WARRIOR_MODE) for: 'I need to push harder.'")
    chat_resp_warrior = perplexity_service_mock.generate_chat_response("I need to push harder.", "WARRIOR_MODE")
    print(f"-> Response: {chat_resp_warrior}")

    procrastination_text = "I'm always procrastinating on my leg day workouts."
    print(f"\nUtterance Analysis for: '{procrastination_text}'")
    analysis = perplexity_service_mock.analyze_client_utterance(procrastination_text)
    print(f"-> Analysis: {analysis}")
