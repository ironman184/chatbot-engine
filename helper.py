import logging
import os
import ollama
import ollama
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
        ACCESS_TOKEN = "EAAUkugjRmKkBQMiNaAaFuPUA8jP8eylT3yaj1SAmRIJ4VO4u1Jot923pZAu9QFZAU95SA9nqWASfPUHOZBKNMUhibQ77Isy3IgZBP8ZCk4N1xIuyxYfcDsWyB5SXBCgHaRUxwZAbCaS1hVoUl8diIMU0QEAlCHCFlCbSnLP0Joi7v89iMZAr4gZAQE1qzAtNvM2ZCn0JCzVZCsZAwGAr3tk5mek0Amv54gscSw2gS8UGlWWPJcx0YZAhu0wxUDtA6CUa70CIZCetrFqDbZCEJ7Cht7ZCEKndCS1"
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

def llm_caller(model, system_prompt, user_prompt, temperature, top_p, top_k):
    return ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            options={
                'temperature': temperature,  # Low temperature for deterministic output
                'top_p': top_p,
                'top_k': top_k,
            },
            format='json'  # Request JSON format output
        )

