import json
import yaml
from helper import llm_caller
from prompts import detect_intent_system_prompt
from registry import register

@register
def check_rules(user_message: str, sessionId: str, SESSION: dict):
    print("Checking rules...")
    if sessionId not in SESSION:
        SESSION[sessionId] = {}
        SESSION[sessionId]["current_state"] = "llm_classify"
        SESSION[sessionId]["intent"] = "common"
    else :
        SESSION[sessionId]["intent"] = "common"
    
@register
def llm_detect_intent(user_message: str, sessionId: str, SESSION: dict) -> None:
    confidence_threshold = 0.7
    try:
        response = llm_caller("gemma2:2b", detect_intent_system_prompt, user_message, 0.2, 0.9, 40)
        llm_output = response["message"]["content"]
        classification = json.loads(llm_output)
        if 'category' not in classification or 'intent' not in classification or 'confidence' not in classification:
            raise ValueError("Missing required fields in LLM response")
        
        print(f"LLM Classification Output: {classification}")
        # Ensure confidence is a float between 0 and 1
        confidence = float(classification['confidence'])
        confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
        intent = classification['intent']
    
        if confidence >= confidence_threshold:
            SESSION[sessionId]["intent"] = intent
            with open(f"WORKFLOWS/{intent}.yaml", "r") as f:
                data = yaml.safe_load(f)  
            SESSION[sessionId]["current_state"] = data.get(intent).get("start_at")  
        else:
            SESSION[sessionId]["current_state"] = "detect_intent_fallback"
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"❌ Error parsing LLM response: {e}")
        print(f"Raw LLM output: {llm_output if 'llm_output' in locals() else 'N/A'}")
        SESSION[sessionId]["current_state"] = "detect_intent_fallback"
        
    except Exception as e:
        # Handle other errors (connection, model not found, etc.)
        print(f"❌ Error in LLM intent detection: {str(e)}")
        SESSION[sessionId]["current_state"] = "detect_intent_fallback"
