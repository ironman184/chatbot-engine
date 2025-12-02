import json
from helper import send_message_to_user
from registry import register, ACTIONS
import yaml


async def processMessage(message, SESSIONS):
    print(f"Session Dict {SESSIONS}")
    idUserMessage = fetchIdAndUserMessage(message)
    sessionId = "wa_" + idUserMessage[1]
    userMessage = idUserMessage[0]
    print(f"Processing message from session {sessionId}: {userMessage}")
    print( sessionId not in SESSIONS)
    if sessionId not in SESSIONS:
          with open("WORKFLOWS/common.yaml", "r") as f:
                data = yaml.safe_load(f)
          current_state = data.get("common").get("states").get("rule_check")      
          handle_flow(current_state, sessionId, userMessage, SESSIONS)
    else:
         intent = SESSIONS.get(sessionId).get("intent")
         with open(f"WORKFLOWS/{intent}.yaml", "r") as f:
            data = yaml.safe_load(f)
         current_state = data.get(intent).get("states").get(SESSIONS.get(sessionId).get("current_state"))
         handle_flow(current_state, sessionId, userMessage, SESSIONS)
         
    
def fetchIdAndUserMessage(body):
    if isinstance(body, str):
        body = json.loads(body)
    wa_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if isinstance(message["text"], dict):
        message_body = message["text"]["body"]
    else:
        message_body = message["text"]
    print(message_body, wa_id )
    return [message_body, wa_id]

def handle_flow(current_state, sessionId, userMessage, SESSIONS):
        current_state_type = current_state.get("type")
        while current_state_type == "action":
            print(SESSIONS)
            action_name = current_state.get("action")
            action_function = ACTIONS.get(action_name)
            if action_function:
                action_function(userMessage, sessionId, SESSIONS)
                sessionDetails = SESSIONS.get(sessionId, {})
                next_state_name = sessionDetails.get("current_state")
                intent = sessionDetails.get("intent")
                with open(f"WORKFLOWS/{intent}.yaml", "r") as f:
                    data = yaml.safe_load(f)
                current_state = data.get(intent).get("states").get(next_state_name)
                current_state_type = current_state.get("type")
            else:
                print(f"❌ Action '{action_name}' not found in registry.")
                break 
            

        if current_state_type == "ask":
            print(f"Asking user")
            send_message_to_user(sessionId, current_state.get("message"))
            current_state = current_state.get("next")
            SESSIONS.get(sessionId)["current_state"] = current_state
            # print(f"Message to user: {current_state.get("message")}")
        elif current_state_type == "ask_buttons":
            print(f"Asking user with buttons")
        elif current_state_type == "reply":
            print("Replying to user")

