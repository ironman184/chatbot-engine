import json
from typing import Dict, Any
import ollama
from registry import register

@register
def check_rules():
    print("Checking common rules...")

###############################################################################
# LLM-Based Intent Detection
###############################################################################

@register
def llm_detect_intent(user_message: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Detect intent and category from user message using Llama 3.1 8B via Ollama.
    
    This function uses a large language model to classify user messages into
    predefined categories and intents, returning a confidence score for the
    classification.
    
    Args:
        user_message (str): The user's input message to classify
        confidence_threshold (float): Minimum confidence score for high confidence
                                     classification (default: 0.7)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - category (str): The classified category
            - intent (str): The specific intent within the category
            - confidence (float): Confidence score between 0.0 and 1.0
            - is_confident (bool): Whether confidence exceeds threshold
            - raw_message (str): Original user message (for debugging)
    
    Example:
        >>> result = llm_detect_intent("Where is my order #12345?")
        >>> print(result)
        {
            "category": "Order Related",
            "intent": "order_status",
            "confidence": 0.95,
            "is_confident": True,
            "raw_message": "Where is my order #12345?"
        }
    """
    
    # Construct the comprehensive system prompt with all categories and intents
    system_prompt = """You are an expert intent classification system for a customer care chatbot. Your job is to analyze user messages and classify them into the correct category and intent.

**Your Task:**
1. Read the user's message carefully
2. Identify the primary category and specific intent
3. Assess your confidence level (0.0 to 1.0)
4. Return ONLY a JSON object with the classification

**Available Categories and Intents:**

**Order Related:**
- order_status: User asking about order status/tracking
- order_missing_items: Items missing from delivered order
- order_not_received: Order not received yet
- order_modify: Want to modify existing order
- cancel_order: Want to cancel an order
- duplicate_order_query: Asking about duplicate orders
- change_delivery_slot: Want to change delivery time
- delivery_partner_issue: Issue with delivery person

**Returns & Exchanges:**
- return_order: Want to return an order
- exchange_order: Want to exchange items
- return_eligibility_check: Checking if item can be returned
- return_policy_query: Asking about return policies
- initiate_return: Starting return process
- wrong_item_received: Received wrong item
- defective_item: Item is damaged or defective
- quality_issue: Quality problems with product
- missing_refund_after_return: Refund not received after return

**Refunds:**
- refund_status: Checking refund status
- refund_method: How refund will be processed
- partial_refund_query: Asking about partial refunds
- refund_initiation: Starting refund process
- refund_not_received: Refund not received

**Delivery & Shipping:**
- shipping_status: Where is the shipment
- change_address: Want to change delivery address
- delivery_date_query: When will order arrive
- delivery_failed: Delivery attempt failed
- shipping_cost: Asking about shipping charges
- shipping_policy: Shipping policies and options
- delivery_speed: Express/fast delivery options
- lost_package: Package lost in transit
- courier_issue: Problem with courier service

**Product Related:**
- product_availability: Is product in stock
- product_size: Size information
- product_color: Color options
- product_specs: Technical specifications
- product_recommendation: Suggest products
- product_material: Material information
- product_care_instructions: How to care for product
- product_warranty: Warranty information
- product_comparison: Compare products
- product_compatibility: Compatibility questions

**Payment & Billing:**
- payment_options: Available payment methods
- cod_availability: Cash on delivery availability
- discount_code_issue: Discount code not working
- invoice_request: Need invoice/bill
- duplicate_payment: Charged twice
- wallet_payment_issue: Wallet payment problems
- subscription_billing_issue: Subscription payment issues
- login_issue: Can't log in

**Account & Profile:**
- reset_password: Reset/forgot password
- update_profile: Update account details
- view_orders: See order history
- delete_account: Close/delete account
- verify_email: Email verification
- verify_phone: Phone verification

**Policies & Info:**
- return_policy: Return policy details
- refund_policy: Refund policy details
- shipping_policy: Shipping policy details
- terms_and_conditions: Terms of service
- privacy_policy: Privacy policy
- warranty_info: Warranty information
- store_hours: Store timings
- store_location: Store address/location

**Technical Issues:**
- website_not_working: Website problems
- payment_gateway_issue: Payment processing issues
- app_issue: Mobile app problems
- cart_issue: Shopping cart issues
- checkout_issue: Can't complete checkout
- talk_to_agent: Want to speak to human agent

**Support:**
- escalation_request: Escalate to supervisor
- feedback: Provide feedback
- complaint: File a complaint

**Small Talk:**
- greeting: Hello, hi, hey
- thanks: Thank you, appreciation
- goodbye: Bye, see you
- smalltalk_general: Casual conversation

**Feedback:**
- positive_feedback: Happy with service
- negative_feedback: Unhappy with service

**Output Format (STRICT JSON ONLY):**
{
  "category": "Category Name",
  "intent": "intent_name",
  "confidence": 0.85
}

**Confidence Guidelines:**
- 0.9-1.0: Very clear and unambiguous intent
- 0.7-0.89: Clear intent with minor ambiguity
- 0.5-0.69: Moderate confidence, some uncertainty
- 0.3-0.49: Low confidence, multiple possible intents
- 0.0-0.29: Very uncertain or unclear

**Important Rules:**
1. Return ONLY valid JSON, no explanations
2. Use exact category and intent names from the list above
3. Be honest about confidence - don't overestimate
4. If message is very unclear, use lower confidence
5. Consider context and common customer service scenarios

Now classify this user message:"""

    try:
        # Call Ollama API with Llama 3.1 8B model
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
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
        
        # Extract the response content
        llm_output = response['message']['content']
        
        # Parse the JSON response
        classification = json.loads(llm_output)
        
        # Validate required fields
        if 'category' not in classification or 'intent' not in classification or 'confidence' not in classification:
            raise ValueError("Missing required fields in LLM response")
        
        # Ensure confidence is a float between 0 and 1
        confidence = float(classification['confidence'])
        confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
        
        # Build the result
        result = {
            'category': classification['category'],
            'intent': classification['intent'],
            'confidence': confidence,
            'is_confident': confidence >= confidence_threshold,
            'raw_message': user_message
        }
        
        print(f"✅ Intent detected: {result['category']} -> {result['intent']} (confidence: {confidence:.2f})")
        return result
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"❌ Error parsing LLM response: {e}")
        print(f"Raw LLM output: {llm_output if 'llm_output' in locals() else 'N/A'}")
        return {
            'category': 'Support',
            'intent': 'talk_to_agent',
            'confidence': 0.0,
            'is_confident': False,
            'raw_message': user_message,
            'error': 'JSON parsing failed'
        }
        
    except Exception as e:
        # Handle other errors (connection, model not found, etc.)
        print(f"❌ Error in LLM intent detection: {str(e)}")
        return {
            'category': 'Support',
            'intent': 'talk_to_agent',
            'confidence': 0.0,
            'is_confident': False,
            'raw_message': user_message,
            'error': str(e)
        }

###############################################################################