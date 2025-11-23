from fastapi import FastAPI, Request, Response, HTTPException
from datetime import datetime
import requests
import json
app = FastAPI()
import logging
import os



SESSIONS = {}
VERIFY_TOKEN="1234567"
@app.get("/")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED")
        return Response(content=challenge, media_type="text/plain", status_code=200)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

def send_message(data):
    print('sending message...', data, os.getenv('ACCESS_TOKEN'))
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
    }

    url = f"https://graph.facebook.com/v22.0/899703906555896/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return {"status": "error", "message": "Request timed out"}, 408
        # return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return {"status": "error", "message": "Failed to send message"}, 500
        # return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        # log_http_response(response)
        return response

@app.post("/")
async def root_function(request: Request):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = await request.json()

        print(f"\n\nWebhook received {timestamp}\n")
        msg = json.dumps(body, indent=2)
        # print("MESSAGE => ",msg)
    except Exception as e:
        print("Exception Raised",e)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)