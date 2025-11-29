"""
Test script for llm_detect_intent function

This script tests the LLM-based intent detection with various sample messages
across different categories to verify the implementation.
"""

import sys
import os

# Add parent directory to path to import from actions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.common_actions import llm_detect_intent

# Test cases covering different categories
test_messages = [
    # Order Related
    "Where is my order #12345?",
    "I want to cancel my order",
    "Can I change my delivery time?",
    
    # Returns & Exchanges
    "I need to return this item",
    "The item I received is damaged",
    
    # Refunds
    "When will I get my refund?",
    "I haven't received my refund yet",
    
    # Delivery & Shipping
    "How much is shipping?",
    "When will my package arrive?",
    
    # Product Related
    "Is this product available in blue?",
    "What size should I order?",
    
    # Payment & Billing
    "Do you accept cash on delivery?",
    "My discount code isn't working",
    
    # Account & Profile
    "I forgot my password",
    "How do I update my email?",
    
    # Support
    "I want to speak to a manager",
    
    # Small Talk
    "Hello!",
    "Thank you so much",
    
    # Ambiguous
    "I need help",
    "Something is wrong",
]

def test_intent_detection():
    """Run tests on all sample messages"""
    print("=" * 80)
    print("LLM Intent Detection Test Suite")
    print("=" * 80)
    print()
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[Test {i}/{len(test_messages)}]")
        print(f"Message: '{message}'")
        print("-" * 80)
        
        try:
            result = llm_detect_intent(message)
            results.append((message, result))
            
            print(f"✓ Category: {result['category']}")
            print(f"✓ Intent: {result['intent']}")
            print(f"✓ Confidence: {result['confidence']:.2%}")
            print(f"✓ Is Confident: {result['is_confident']}")
            
            if 'error' in result:
                print(f"⚠ Error: {result['error']}")
                
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append((message, None))
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    successful = sum(1 for _, r in results if r is not None and 'error' not in r)
    high_confidence = sum(1 for _, r in results if r is not None and r.get('is_confident', False))
    
    print(f"Total tests: {len(test_messages)}")
    print(f"Successful: {successful}")
    print(f"High confidence (≥0.7): {high_confidence}")
    print(f"Low confidence (<0.7): {successful - high_confidence}")
    
    # Show high confidence results
    print("\n" + "=" * 80)
    print("High Confidence Classifications")
    print("=" * 80)
    for msg, result in results:
        if result and result.get('is_confident', False):
            print(f"• '{msg[:50]}...' → {result['category']} / {result['intent']} ({result['confidence']:.0%})")

if __name__ == "__main__":
    print("⚙️  Starting intent detection tests...")
    print("⚙️  Make sure Ollama is running with llama3.1:8b model\n")
    
    try:
        test_intent_detection()
        print("\n✅ All tests completed!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
