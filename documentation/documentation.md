# Chatbot Engine Documentation

## Change Log

### 28 November 2025 - LLM Intent Detection Implementation

**Feature Added:** LLM-based intent classification using Ollama and Llama 3.1 8B

**File Modified:** `actions/common_actions.py`

**Changes:**
- Implemented complete `llm_detect_intent()` function with the following capabilities:
  - Accepts `user_message` (str) and optional `confidence_threshold` (float, default 0.7)
  - Uses Ollama with Llama 3.1 8B model for classification
  - Returns structured dict with: category, intent, confidence, is_confident flag
  - Comprehensive system prompt covering all 12 categories and 100+ intents
  - Low temperature (0.2) for deterministic, consistent results
  - Robust error handling for JSON parsing and API failures
  - Confidence thresholding to trigger fallback flows
  - Detailed logging for debugging

**Categories Supported:**
1. Order Related (8 intents)
2. Returns & Exchanges (9 intents)
3. Refunds (5 intents)
4. Delivery & Shipping (9 intents)
5. Product Related (10 intents)
6. Payment & Billing (8 intents)
7. Account & Profile (6 intents)
8. Policies & Info (8 intents)
9. Technical Issues (6 intents)
10. Support (3 intents)
11. Small Talk (4 intents)
12. Feedback (2 intents)

**Return Format:**
```python
{
    "category": str,        # Classified category name
    "intent": str,          # Specific intent identifier
    "confidence": float,    # Score between 0.0 and 1.0
    "is_confident": bool,   # True if confidence >= threshold
    "raw_message": str      # Original user message
}
```

**Error Handling:**
- Falls back to `talk_to_agent` intent on errors
- Sets confidence to 0.0 and is_confident to False
- Includes error details in response for debugging

**Integration:**
- Works with existing workflow system (WORKFLOWS/common.yaml)
- High confidence: proceeds to intent-specific flow
- Low confidence: triggers fallback/main menu

**Prerequisites:**
- Ollama must be running locally
- Llama 3.1 8B model must be installed: `ollama pull llama3.1:8b`

**Dependencies:**
- ollama==0.6.1 (already in requirements.txt)

---
