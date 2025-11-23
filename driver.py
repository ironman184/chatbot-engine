import json
from typing import Optional
from fastapi import FastAPI
from session import get_session
from session import save_session
from session import clear_session
from registry import register
from registry import ACTIONS
import yaml

sessionDetails = {
    "intent": "order_status",
    
    "current_state": "validate_order_id",

    "data": {
        "order_id": "45310",
        "last4_digits": None,
        "otp_verified": False
    },

    "last_message_time": 1700000000,  # optional
}

async def processMessage(message, SESSIONS):
    idUserMessage = fetchIdAndUserMessage(message)
    sessionId = "wa_" + idUserMessage[1]
    userMessage = idUserMessage[0]
    sessionDetails = get_session(SESSIONS, sessionId)
    if sessionDetails is None:
          with open("WORKFLOWS/common.yaml", "r") as f:
                data = yaml.safe_load(f)
          current_step = data.get("common").get("states").get("rule_check")      
          handleFlow(current_step, sessionDetails, userMessage)
    else:
         intent = sessionDetails["intent"]
         with open(intent + ".yaml", "r") as f:
                data = yaml.safe_load(f)    
         current_state = sessionDetails["current_state"]
         state_details = data["states"][current_state]
        
    
def fetchIdAndUserMessage(body):
    if isinstance(body, str):
        body = json.loads(body)
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if isinstance(message["text"], dict):
        message_body = message["text"]["body"]
    else:
        message_body = message["text"]
    print(message_body, wa_id )
    return [message_body, wa_id]

def handleFlow(current_step, sessionDetails, userMessage):
    while(current_step.get("type") == "action"):
        current_step_type = current_step.get("type")
        if current_step_type == "action":
            print(f"Executing action")
        elif current_step_type == "ask":
            print(f"Asking user")
        elif current_step_type == "ask_buttons":
            print(f"Asking user with buttons")
        elif current_step_type == "reply":
            print("Replying to user")

