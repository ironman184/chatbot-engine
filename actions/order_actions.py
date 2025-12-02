import ollama
from registry import register
from shopify_client import ShopifyGraphQLClient
from shopify_queries import GET_ORDER_DETAILS
from prompts import extract_order_id_system_prompt, generate_order_update_system_prompt
from helper import send_message_to_user
import json


def pretty_print(data: dict) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))

@register
def fetch_order_details(user_message: str, sessionId: str, SESSION: dict):
    print("Fetching order details from Shopify...")
    order_id = ""
    if SESSION.get(sessionId, {}).get("data", {}).get("order_id"):
        order_id = SESSION[sessionId]["data"]["order_id"]
    else:
        order_id = user_message.strip()    
    client = ShopifyGraphQLClient("https://wave-wrist.myshopify.com", "")
    sessionDetails = SESSION.get(sessionId, {})
    
    try:
        order_details = client.query(GET_ORDER_DETAILS, variables={"name": f"name:{order_id}"})
        
        # Check if order exists (has edges)
        if order_details.get("orders", {}).get("edges"):
            # ✅ ORDER FOUND - Extract and store details
            order_node = order_details["orders"]["edges"][0]["node"]
            
            if "data" not in sessionDetails:
                sessionDetails["data"] = {}
            
            sessionDetails["data"]["order_id"] = order_id
            sessionDetails["data"]["order_details"] = order_node
            sessionDetails["current_state"] = "verify_customer"
            print(f"✅ Order {order_id} found and details stored.")
            pretty_print(order_details)
        else:
            # ❌ ORDER NOT FOUND
            print(f"❌ Order {order_id} not found in Shopify")
            sessionDetails["current_state"] = "ask_order_id_or_other"
        
    except Exception as e:
        # ❌ API ERROR
        print(f"❌ Error fetching order: {str(e)}")
        sessionDetails["current_state"] = "ask_order_id_or_other"

@register
def extract_order_id(user_message: str, sessionId: str, SESSION: dict) -> None:
    print("Extracting order ID from user message...")
    try:
        response = ollama.chat(
            model='gemma2:2b',
            messages=[
                {
                    'role': 'system',
                    'content': extract_order_id_system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            options={
                'temperature': 0.2,  # Low temperature for deterministic output
                'top_p': 0.9,
                'top_k': 40,
            },
            format='json'  # Request JSON format output
        )
        llm_output = response['message']['content']
        classification = json.loads(llm_output)
        order_id = classification.get("order_name", None)
        sessionDetails = SESSION.get(sessionId, {})

        if order_id:
            if "data" not in sessionDetails:
                sessionDetails["data"] = {}
            
            sessionDetails["data"]["order_id"] = order_id
            sessionDetails["current_state"] = "fetch_order_details"
            
            print(f"✅ Order ID extracted and stored: {order_id}")
        else:
            sessionDetails["current_state"] = "ask_order_id"
            print("❌ No valid order ID found in the message.")

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing LLM response: {e}")
        sessionDetails["current_state"] = "ask_order_id"
    
    except Exception as e:
        print(f"❌ Error extracting order ID: {str(e)}")
        sessionDetails["current_state"] = "ask_order_id"

@register
def verify_customer(user_message: str, sessionId: str, SESSION: dict)-> None:
    print("Verifying customer...")
    sessionDetails = SESSION.get(sessionId, {})
    sessionDetails["current_state"] = "provide_order_update"


@register
def generate_order_update(user_message: str, sessionId: str, SESSION: dict)-> None:
    print("Generating order update...")
    sessionDetails = SESSION.get(sessionId, {})
    order_details = sessionDetails.get("data", {}).get("order_details", {})
    user_prompt = f"""
        Order data:
        {json.dumps(order_details, indent=2)}
        User question:
        {user_message}"""
    try:
        response = ollama.chat(
            model='gemma2:2b',
            messages=[
                {
                    'role': 'system',
                    'content': generate_order_update_system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            options={
                'temperature': 0.1,  # Low temperature for deterministic output
                'top_p': 0.8,
                'top_k': 40,
            },
            format='json'  # Request JSON format output
        )
        llm_output = response['message']['content']
        classification = json.loads(llm_output)
        reply = classification.get("reply", "I'm sorry, I couldn't generate an update for your order.")
        SESSION.get(sessionId)["current_state"] = ""
        send_message_to_user(sessionId, reply)

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing LLM response: {e}")
        sessionDetails["current_state"] = ""
    
    except Exception as e:
        print(f"❌ Error extracting order ID: {str(e)}")
        sessionDetails["current_state"] = ""
    
    
   