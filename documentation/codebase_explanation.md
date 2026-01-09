## 🏗️ High-Level Architecture

This is a **WhatsApp chatbot** that helps customers with orders from a Shopify store. The flow is:

1. **WhatsApp** → User sends a message
2. **Meta Cloud API** → Forwards message to your webhook
3. **FastAPI Server** (chat.py) → Receives webhook
4. **Intent Detection** → Figures out what user wants
5. **Workflow Engine** → Executes appropriate conversation flow
6. **Shopify API** → Fetches order/customer data if needed
7. **Response Generation** → Creates helpful reply
8. **WhatsApp** → Sends response back to user

---

## 📋 Detailed Flow Breakdown

### **Step 1: Message Reception** (chat.py)

When a WhatsApp message arrives:

```python
@app.post("/")
async def root_function(request: Request):
    # 1. Receive webhook from WhatsApp
    body = await request.json()
    
    # 2. Check if it's a delivery status (ignore these)
    if "statuses" in body["entry"][0]["changes"][0]["value"]:
        return JSONResponse(status_code=200, content={"status": "received"})
    
    # 3. Process actual user messages
    asyncio.create_task(processMessage(msg, SESSIONS))
    
    # 4. Immediately acknowledge to WhatsApp (200 OK)
    return JSONResponse(status_code=200, content={"status": "received"})
```

**Why the quick acknowledgment?** WhatsApp requires a response within 5 seconds, so we process the message asynchronously.

---

### **Step 2: Message Processing** (driver.py)

The `processMessage` function extracts user info and routes to the workflow engine:

```python
async def processMessage(message, SESSIONS):
    # 1. Extract phone number and message text
    idUserMessage = fetchIdAndUserMessage(message)
    sessionId = "wa_" + idUserMessage[1]  # e.g., "wa_919718326464"
    userMessage = idUserMessage[0]        # e.g., "Where is my order?"
    
    # 2. Check if this is a new conversation
    if sessionId not in SESSIONS:
        # Load common workflow for new users
        with open("WORKFLOWS/common.yaml", "r") as f:
            data = yaml.safe_load(f)
        current_state = data.get("common").get("states").get("rule_check")
        handle_flow(current_state, sessionId, userMessage, SESSIONS)
    else:
        # Continue existing conversation
        intent = SESSIONS[sessionId]["intent"]
        current_state_name = SESSIONS[sessionId]["current_state"]
        # Load intent-specific workflow
        with open(f"WORKFLOWS/{intent}.yaml", "r") as f:
            data = yaml.safe_load(f)
        current_state = data.get(intent).get("states").get(current_state_name)
        handle_flow(current_state, sessionId, userMessage, SESSIONS)
```

**Key Concept:** Each user has a `sessionId` (their WhatsApp number) that tracks their conversation state in the `SESSIONS` dictionary.

---

### **Step 3: Workflow Engine** (driver.py)

The `handle_flow` function is the **heart of the system**. It processes workflow states:

```python
def handle_flow(current_state, sessionId, userMessage, SESSIONS):
    current_state_type = current_state.get("type")
    
    # Execute all consecutive 'action' states
    while current_state_type == "action":
        action_name = current_state.get("action")
        action_function = ACTIONS.get(action_name)  # Lookup from registry
        
        if action_function:
            # Execute the action
            action_function(userMessage, sessionId, SESSIONS)
            
            # Get next state from session (action modifies it)
            next_state_name = SESSIONS[sessionId]["current_state"]
            intent = SESSIONS[sessionId]["intent"]
            
            # Load next state
            with open(f"WORKFLOWS/{intent}.yaml", "r") as f:
                data = yaml.safe_load(f)
            current_state = data.get(intent).get("states").get(next_state_name)
            current_state_type = current_state.get("type")
        else:
            break
    
    # Handle user interaction states
    if current_state_type == "ask":
        send_message_to_user(sessionId, current_state.get("message"))
        SESSIONS[sessionId]["current_state"] = current_state.get("next")
```

**State Types:**
- **`action`**: Execute Python function (e.g., fetch data, detect intent)
- **`ask`**: Send message and wait for user reply
- **`ask_buttons`**: Send message with button options
- **`reply`**: Send final message and end conversation

---

### **Step 4: Intent Detection** (actions/common_actions.py)

When a new message arrives, the system determines what the user wants:

#### **4a. Rule-Based Check** (`check_rules`)

```python
@register
def check_rules(user_message: str, sessionId: str, SESSION: dict):
    # Initialize session if new
    if sessionId not in SESSION:
        SESSION[sessionId] = {}
        SESSION[sessionId]["current_state"] = "llm_classify"
        SESSION[sessionId]["intent"] = "common"
```

This is a placeholder for simple pattern matching (e.g., "hello" → greeting). Currently, it always falls through to LLM classification.

#### **4b. LLM Classification** (`llm_detect_intent`)

Uses a local LLM (Gemma 2:2B via Ollama) to understand user intent:

```python
@register
def llm_detect_intent(user_message: str, sessionId: str, SESSION: dict) -> None:
    # 1. Call LLM with specialized prompt
    response = llm_caller("gemma2:2b", detect_intent_system_prompt, user_message, ...)
    llm_output = response["message"]["content"]
    
    # 2. Parse JSON response
    classification = json.loads(llm_output)
    # Example: {"category": "Order Related", "intent": "order_inquiry", "confidence": 0.95}
    
    # 3. Check confidence threshold
    if confidence >= 0.7:
        # High confidence - route to intent-specific workflow
        SESSION[sessionId]["intent"] = "order_inquiry"  # or other intent
        SESSION[sessionId]["current_state"] = "order_id_extraction"
    else:
        # Low confidence - show fallback menu
        SESSION[sessionId]["current_state"] = "detect_intent_fallback"
```

**Why LLM?** More flexible than keyword matching. Can understand variations like:
- "Where's my order?"
- "Track my package"
- "Order status for #1001"

All map to `order_inquiry` intent.

---

### **Step 5: Order Inquiry Workflow** (WORKFLOWS/order_inquiry.yaml)

Once intent is detected as `order_inquiry`, the workflow executes:

```yaml
order_inquiry:
  start_at: order_id_extraction
  states:
    order_id_extraction:
      type: action
      action: "extract_order_id"
      on_found: fetch_order_details
      on_not_found: ask_order_id
```

#### **5a. Extract Order ID** (`extract_order_id`)

```python
@register
def extract_order_id(user_message: str, sessionId: str, SESSION: dict) -> None:
    # Use LLM to find order ID in message
    response = llm_caller("gemma2:2b", extract_order_id_system_prompt, user_message, ...)
    classification = json.loads(response["message"]["content"])
    # Example: {"order_name": "#1001"} or {"order_name": null}
    
    order_id = classification.get("order_name", None)
    
    if order_id:
        # Store in session
        SESSION[sessionId]["data"]["order_id"] = order_id
        SESSION[sessionId]["current_state"] = "fetch_order_details"
    else:
        # Need to ask user
        SESSION[sessionId]["current_state"] = "ask_order_id"
```

**Why LLM?** Can extract order IDs from natural language:
- "My order #1001 hasn't arrived" → extracts `#1001`
- "I'm waiting for EN1001-A" → extracts `EN1001-A`

#### **5b. Fetch Order Details** (`fetch_order_details`)

```python
@register
def fetch_order_details(user_message: str, sessionId: str, SESSION: dict):
    # Get order ID from session or user message
    order_id = SESSION[sessionId]["data"]["order_id"]
    
    # Query Shopify GraphQL API
    client = ShopifyGraphQLClient("https://wave-wrist.myshopify.com", ACCESS_TOKEN)
    order_details = client.query(GET_ORDER_DETAILS, variables={"name": f"name:{order_id}"})
    
    if order_details.get("orders", {}).get("edges"):
        # Order found - store in session
        order_node = order_details["orders"]["edges"][0]["node"]
        SESSION[sessionId]["data"]["order_details"] = order_node
        SESSION[sessionId]["current_state"] = "verify_customer"
    else:
        # Order not found
        SESSION[sessionId]["current_state"] = "ask_order_id_or_other"
```

**GraphQL Query** (shopify_queries.py) fetches:
- Order status (paid, pending, cancelled)
- Fulfillment status (unfulfilled, fulfilled, shipped)
- Tracking info (number, URL, estimated delivery)
- Line items (products ordered)
- Customer info (name, email, phone)
- Shipping address

#### **5c. Verify Customer** (`verify_customer`)

```python
@register
def verify_customer(user_message: str, sessionId: str, SESSION: dict) -> None:
    # Currently a placeholder - would check if WhatsApp number matches order
    SESSION[sessionId]["current_state"] = "provide_order_update"
```

**Future Enhancement:** Compare WhatsApp number with order phone number for security.

#### **5d. Generate Response** (`generate_order_update`)

```python
@register
def generate_order_update(user_message: str, sessionId: str, SESSION: dict) -> None:
    order_details = SESSION[sessionId]["data"]["order_details"]
    
    # Use LLM to generate natural language response
    user_prompt = f"""
        Order data: {json.dumps(order_details, indent=2)}
        User question: {user_message}
    """
    
    response = llm_caller("gemma2:2b", generate_order_update_system_prompt, user_prompt, ...)
    classification = json.loads(response["message"]["content"])
    # Example: {"reply": "Your order #1001 was shipped on Jan 15...", "confidence": "high"}
    
    reply = classification.get("reply", "I'm sorry, I couldn't generate an update.")
    send_message_to_user(sessionId, reply)
```

**Why LLM for Response?** Converts structured order data into conversational text:

**Input:**
```json
{
  "name": "#1001",
  "displayFulfillmentStatus": "FULFILLED",
  "trackingInfo": {"number": "1234567890", "url": "https://track.com/..."}
}
```

**Output:**
> "Good news! Your order #1001 has been shipped. You can track it here: https://track.com/... The estimated delivery is Jan 20."

---

### **Step 6: Sending Response** (helper.py)

```python
def send_message_to_user(sessionId, message):
    user_phone = sessionId.replace("wa_", "")  # Extract phone number
    
    # WhatsApp Cloud API payload
    data = {
        "messaging_product": "whatsapp",
        "to": user_phone,
        "type": "text",
        "text": {"body": message}
    }
    
    # Send via Meta Graph API
    response = requests.post(
        "https://graph.facebook.com/v22.0/899703906555896/messages",
        json=data,
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
```

---

## 🔑 Key Design Patterns

### **1. Action Registry** (registry.py)

All action functions are registered in a global dictionary:

```python
ACTIONS = {}

def register(fn):
    ACTIONS[fn.__name__] = fn
    return fn

# Usage:
@register
def fetch_order_details(...):
    ...
```

**Why?** Workflows reference actions by name (strings in YAML). The registry maps names to actual Python functions.

### **2. Session State Management** (session.py)

Each user's conversation state is stored in memory:

```python
SESSIONS = {
    "wa_919718326464": {
        "intent": "order_inquiry",
        "current_state": "fetch_order_details",
        "data": {
            "order_id": "#1001",
            "order_details": {...}
        }
    }
}
```

**Structure:**
- `intent`: Current workflow (e.g., `order_inquiry`, `common`)
- `current_state`: Current step in workflow
- `data`: Context data (order ID, customer info, etc.)

### **3. YAML-Driven Workflows** (WORKFLOWS/)

Conversation flows are defined in YAML, not hardcoded:

```yaml
order_inquiry:
  start_at: order_id_extraction
  states:
    order_id_extraction:
      type: action
      action: "extract_order_id"
      on_found: fetch_order_details
      on_not_found: ask_order_id
    
    ask_order_id:
      type: ask
      message: "Could you please share your order ID?"
      next: fetch_order_details
```

**Benefits:**
- Easy to modify flows without code changes
- Non-developers can update conversation scripts
- Clear visual representation of logic

### **4. LLM Integration** (helper.py)

All LLM calls go through a single function:

```python
def llm_caller(model, system_prompt, user_prompt, temperature, top_p, top_k):
    return ollama.chat(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        options={'temperature': temperature, 'top_p': top_p, 'top_k': top_k},
        format='json'  # Forces JSON output
    )
```

**Why Centralized?** Consistent error handling, logging, and easy model swapping.

---

## 🔄 Complete Example Flow

**User:** "Where is my order #1001?"

1. **WhatsApp → FastAPI** (chat.py)
   - Webhook receives message
   - Extracts: `sessionId = "wa_919718326464"`, `userMessage = "Where is my order #1001?"`

2. **Session Check** (driver.py)
   - `sessionId` not in `SESSIONS` → new conversation
   - Loads common.yaml
   - Starts at `rule_check` state

3. **Rule Check** (actions/common_actions.py)
   - No rules matched
   - Sets `current_state = "llm_classify"`

4. **LLM Intent Detection** (actions/common_actions.py)
   - Calls Gemma 2:2B
   - Returns: `{"category": "Order Related", "intent": "order_inquiry", "confidence": 0.95}`
   - Confidence ≥ 0.7 → route to `order_inquiry` workflow
   - Sets `SESSION[sessionId]["intent"] = "order_inquiry"`
   - Loads order_inquiry.yaml
   - Sets `current_state = "order_id_extraction"`

5. **Extract Order ID** (actions/order_actions.py)
   - Calls LLM
   - Extracts: `{"order_name": "#1001"}`
   - Stores in session: `SESSION[sessionId]["data"]["order_id"] = "#1001"`
   - Sets `current_state = "fetch_order_details"`

6. **Fetch from Shopify** (actions/order_actions.py)
   - GraphQL query to Shopify
   - Order found → stores details in session
   - Sets `current_state = "verify_customer"`

7. **Verify Customer** (actions/order_actions.py)
   - (Placeholder) Assumes verified
   - Sets `current_state = "provide_order_update"`

8. **Generate Response** (actions/order_actions.py)
   - Calls LLM with order data + user question
   - LLM returns: `{"reply": "Your order #1001 was shipped on Jan 15. Track it here: ...", "confidence": "high"}`
   - Sends reply via WhatsApp

9. **User Receives:**
   > "Your order #1001 was shipped on Jan 15. Track it here: https://track.com/1234567890. Estimated delivery: Jan 20."

---

# 🚀 How to Run This Codebase

## Prerequisites

### 1. **Python Environment**

```bash
# Create virtual environment
python3 -m venv myenv

# Activate it
source myenv/bin/activate  # macOS/Linux
# OR
myenv\Scripts\activate  # Windows
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi==0.122.0` - Web framework
- `requests==2.32.5` - HTTP client
- `uvicorn==0.38.0` - ASGI server
- `PyYAML==6.0.3` - YAML parser
- `ollama==0.6.1` - LLM client

### 3. **Install Ollama (Local LLM)**

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/download)

**Pull the model:**
```bash
ollama pull gemma2:2b
```

**Start Ollama service:**
```bash
ollama serve
```

### 4. **WhatsApp Business API Setup**

You need:
- **Meta Business Account** (free)
- **WhatsApp Business Phone Number**
- **Access Token** (from Meta Developer Console)

**Steps:**
1. Go to [Meta Developer Console](https://developers.facebook.com/)
2. Create app → Select "Business" type
3. Add "WhatsApp" product
4. Generate a test phone number (free)
5. Copy:
   - **Phone Number ID** (e.g., `899703906555896`)
   - **Access Token** (starts with `EAAU...`)

**Update in helper.py:**
```python
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
url = f"https://graph.facebook.com/v22.0/YOUR_PHONE_NUMBER_ID/messages"
```

### 5. **Shopify Store Setup**

You need:
- **Shopify Store** (can use free trial)
- **Admin API Access Token**

**Steps:**
1. Go to Shopify Admin → Settings → Apps and sales channels
2. Develop apps → Create custom app
3. Configure → Admin API scopes:
   - `read_orders`
   - `read_customers`
4. Install app → Copy **Admin API access token**

**Update in order_actions.py:**
```python
client = ShopifyGraphQLClient(
    "https://YOUR-STORE.myshopify.com",
    "YOUR_SHOPIFY_ACCESS_TOKEN"
)
```

---

## Running Locally

### **Option 1: Test with Sample Data** (main.py)

```bash
python main.py
```

This:
- Loads message_1.json (sample WhatsApp message)
- Processes it through the workflow
- Prints output to console (doesn't send to WhatsApp)

**Useful for:** Debugging workflows without WhatsApp setup.

### **Option 2: Run as Webhook** (chat.py)

```bash
python chat.py
# OR
uvicorn chat:app --reload --host 0.0.0.0 --port 8000
```

Server starts at `http://localhost:8000`

**Verify endpoint:**
```bash
curl "http://localhost:8000/?hub.mode=subscribe&hub.verify_token=1234567&hub.challenge=test"
```

Should return: `test`

---

## Exposing to WhatsApp (Required for Real Messages)

WhatsApp needs a **public HTTPS URL**. Use one of:

### **Option A: ngrok (Easiest)**

```bash
# Install ngrok
brew install ngrok  # macOS
# OR download from ngrok.com

# Start ngrok tunnel
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### **Option B: Deploy to Cloud**

- **Railway.app** (free tier)
- **Render.com** (free tier)
- **Fly.io** (free tier)

### **Configure WhatsApp Webhook**

1. Go to Meta Developer Console → WhatsApp → Configuration
2. Set **Callback URL**: `https://your-ngrok-url.ngrok.io/`
3. Set **Verify Token**: `1234567` (from chat.py)
4. Click **Verify and Save**
5. Subscribe to **`messages`** webhook field

---

## Testing End-to-End

1. **Send test message from WhatsApp:**
   - Use the test number provided by Meta
   - Send: "Where is my order #1001?"

2. **Check logs:**
   ```
   Webhook received 2025-01-15 10:30:00
   Processing message from session wa_919718326464: Where is my order #1001?
   Checking rules...
   LLM Classification Output: {'category': 'Order Related', 'intent': 'order_inquiry', 'confidence': 0.95}
   Extracting order ID...
   ✅ Order ID extracted: #1001
   Fetching order details from Shopify...
   ✅ Order #1001 found
   Generating order update...
   Sending message to 919718326464: Your order #1001 was shipped...
   ```

3. **Receive reply in WhatsApp:**
   > Your order #1001 was shipped on Jan 15. Track it here: [link]. Estimated delivery: Jan 20.

---

## Common Issues & Solutions

### ❌ "Connection refused to Ollama"

**Solution:**
```bash
ollama serve  # Must be running in background
```

### ❌ "Shopify API error: Unauthorized"

**Solution:**
- Check access token in order_actions.py
- Verify scopes include `read_orders`

### ❌ "WhatsApp message not received"

**Solution:**
- Check ngrok is running: `ngrok http 8000`
- Verify webhook URL in Meta Console
- Check verify token matches (chat.py: `VERIFY_TOKEN="1234567"`)

### ❌ "JSON parsing error in LLM response"

**Solution:**
- LLM sometimes returns malformed JSON
- Lower temperature: `llm_caller(..., temperature=0.1, ...)`
- Use a more capable model: `ollama pull llama3.1:8b`

---

## Project Structure Summary

```
chatbot-engine/
├── chat.py                 # FastAPI webhook server (entry point)
├── main.py                 # Local testing script
├── driver.py               # Workflow engine (state machine)
├── helper.py               # Utility functions (LLM, WhatsApp)
├── registry.py             # Action function registry
├── prompts.py              # LLM system prompts
├── shopify_client.py       # Shopify GraphQL client
├── shopify_queries.py      # GraphQL query templates
├── actions/
│   ├── common_actions.py   # Intent detection, rule checking
│   └── order_actions.py    # Order-related actions
├── WORKFLOWS/
│   ├── common.yaml         # Initial classification workflow
│   └── order_inquiry.yaml  # Order status workflow
└── requirements.txt        # Python dependencies
```

---

## Next Steps

1. **Add more intents** (returns, refunds, product questions)
2. **Implement customer verification** (phone number matching)
3. **Add Qdrant vector DB** (for conversation context/FAQs)
4. **Persistent sessions** (currently in-memory, lost on restart)
5. **Button support** (WORKFLOWS/order_inquiry.yaml has `ask_buttons` state)
6. **Error recovery** (handle API failures gracefully)

---