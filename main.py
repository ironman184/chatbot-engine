import json
from driver import processMessage
import asyncio
from load_actions import load_all_actions

SESSIONS = {}


def load_message(filename: str = "message_1.json"):
	"""Load and return JSON content from `filename` as a Python object."""
	with open(filename, "r", encoding="utf-8") as fh:
		return json.load(fh)

async def main():
    message = load_message("message.json")
    msg = json.dumps(message, indent=2)
    await processMessage(msg, SESSIONS)

if __name__ == "__main__":
    load_all_actions()
    asyncio.run(main())

