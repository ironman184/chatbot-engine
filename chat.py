import asyncio
from fastapi import FastAPI, Request, Response, HTTPException
from datetime import datetime
import json

from fastapi.responses import JSONResponse

from driver import processMessage
from load_actions import load_all_actions

app = FastAPI()

# Load all registered actions at startup
load_all_actions()

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

@app.post("/")
async def root_function(request: Request):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = await request.json()

        print(f"\n\nWebhook received {timestamp}\n")
        msg = json.dumps(body, indent=2)
        if "statuses" in body["entry"][0]["changes"][0]["value"]:
            # This is a delivery status callback, not a message
            return JSONResponse(status_code=200, content={"status": "received"})
        print("MESSAGE => ",msg)
        
         # Process message in background, DO NOT await blocking logic here
        asyncio.create_task(processMessage(msg, SESSIONS))

        # Acknowledge webhook quickly
        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        print("Exception Raised",e)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)