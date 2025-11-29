# LLM Intent Detection - Quick Reference

## Function Overview

The `llm_detect_intent()` function classifies user messages into categories and intents using Llama 3.1 8B via Ollama.

## Usage

```python
from actions.common_actions import llm_detect_intent

# Basic usage with default threshold (0.7)
result = llm_detect_intent("Where is my order?")

# Custom confidence threshold
result = llm_detect_intent("I need help", confidence_threshold=0.8)
```

## Return Value

```python
{
    "category": "Order Related",           # The classified category
    "intent": "order_status",              # Specific intent identifier
    "confidence": 0.95,                    # Float between 0.0 and 1.0
    "is_confident": True,                  # True if confidence >= threshold
    "raw_message": "Where is my order?"    # Original input message
}
```

## Confidence Levels

- **0.9 - 1.0**: Very clear, unambiguous intent
- **0.7 - 0.89**: Clear intent with minor ambiguity (default threshold)
- **0.5 - 0.69**: Moderate confidence
- **0.3 - 0.49**: Low confidence
- **0.0 - 0.29**: Very uncertain

## Integration with Workflows

Based on `WORKFLOWS/common.yaml`:

```yaml
llm_classify:
  type: action
  action: "llm_detect_intent"
  on_high_confidence: move_to_intent_flow    # is_confident == True
  on_low_confidence: llm_fallback            # is_confident == False
```

## Example Classifications

### High Confidence Examples

```python
# Order status query
"Where is my order #12345?"
→ Category: "Order Related", Intent: "order_status", Confidence: 0.95

# Return request
"I want to return this product"
→ Category: "Returns & Exchanges", Intent: "return_order", Confidence: 0.92

# Shipping inquiry
"How much does shipping cost?"
→ Category: "Delivery & Shipping", Intent: "shipping_cost", Confidence: 0.90
```

### Moderate Confidence Examples

```python
# Ambiguous help request
"I need help with something"
→ Category: "Support", Intent: "talk_to_agent", Confidence: 0.65

# Unclear product question
"Tell me about your products"
→ Category: "Product Related", Intent: "product_recommendation", Confidence: 0.70
```

### Low Confidence Examples

```python
# Very vague message
"Something is wrong"
→ Confidence: 0.45, is_confident: False

# Incomplete query
"I want to..."
→ Confidence: 0.30, is_confident: False
```

## Error Handling

The function includes robust error handling:

```python
# On any error (API failure, JSON parsing, etc.)
{
    "category": "Support",
    "intent": "talk_to_agent",
    "confidence": 0.0,
    "is_confident": False,
    "raw_message": "...",
    "error": "Error description"  # Only present on errors
}
```

## Prerequisites

1. **Install Ollama**: Download from https://ollama.ai
2. **Pull the model**:
   ```bash
   ollama pull llama3.1:8b
   ```
3. **Start Ollama**: Ensure the Ollama service is running

## Testing

Run the test suite:

```bash
python test_intent_detection.py
```

This will test classification across all categories with sample messages.

## Supported Categories

1. **Order Related** - order_status, cancel_order, order_modify, etc.
2. **Returns & Exchanges** - return_order, exchange_order, defective_item, etc.
3. **Refunds** - refund_status, refund_not_received, etc.
4. **Delivery & Shipping** - shipping_status, delivery_failed, etc.
5. **Product Related** - product_availability, product_specs, etc.
6. **Payment & Billing** - payment_options, discount_code_issue, etc.
7. **Account & Profile** - reset_password, update_profile, etc.
8. **Policies & Info** - return_policy, shipping_policy, etc.
9. **Technical Issues** - website_not_working, app_issue, etc.
10. **Support** - talk_to_agent, escalation_request, etc.
11. **Small Talk** - greeting, thanks, goodbye
12. **Feedback** - positive_feedback, negative_feedback

## Performance Notes

- **Response Time**: Typically 1-3 seconds (local inference)
- **Model Size**: ~4.7GB (Llama 3.1 8B)
- **Memory Usage**: ~8GB RAM recommended
- **Temperature**: Set to 0.2 for consistent results

## Troubleshooting

### "Connection Error"
- Ensure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`

### "Model not found"
- Pull the model: `ollama pull llama3.1:8b`

### "JSON parsing failed"
- The model returned invalid JSON
- Function automatically falls back to safe defaults
- Check logs for raw LLM output

### Low Confidence on Clear Messages
- May need to adjust temperature or prompt
- Consider adding few-shot examples in the prompt
- Check if intent is in the supported list

## Advanced Configuration

To modify behavior, update the function in `actions/common_actions.py`:

- **Temperature**: Lower = more deterministic (current: 0.2)
- **Threshold**: Default is 0.7, can be changed per call
- **Model**: Currently using `llama3.1:8b`
- **Top-p/Top-k**: Controls diversity (current: 0.9 / 40)

## Integration Example

```python
# In your workflow handler
async def handle_user_message(message: str):
    # Step 1: Detect intent
    result = llm_detect_intent(message)
    
    # Step 2: Check confidence
    if result['is_confident']:
        # High confidence - proceed to intent-specific flow
        intent = result['intent']
        category = result['category']
        await handle_intent(intent, category, message)
    else:
        # Low confidence - show fallback/menu
        await show_main_menu()
```

## Logging

The function prints status messages:
- ✅ Success: `Intent detected: Category -> intent (confidence: 0.95)`
- ❌ Error: `Error in LLM intent detection: ...`
- ❌ Parse error: `Error parsing LLM response: ...`
