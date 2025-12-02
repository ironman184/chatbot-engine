import logging
import os
import requests


def send_message_to_user(sessionId, message):
    try:
        user_phone = sessionId.replace("wa_", "")
        data = {
            "messaging_product": "whatsapp",
            "to": user_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        # Replace with your actual access token
        ACCESS_TOKEN = ""
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }

        url = f"https://graph.facebook.com/v22.0/899703906555896/messages"

        print(f"Sending message to {user_phone}: {message}")
        
        response = requests.post(
            url, 
            json=data,  # Use json= instead of data= for proper serialization
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        
        logging.info(f"Message sent successfully to session {sessionId}")
        return response.json()
        
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return {"status": "error", "message": "Request timed out"}, 408
        
    except requests.RequestException as e:
        logging.error(f"Request failed due to: {e}")
        return {"status": "error", "message": "Failed to send message"}, 500
        
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

