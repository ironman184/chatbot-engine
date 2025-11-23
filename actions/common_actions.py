from registry import register

@register
def check_rules():
    print("Checking common rules...")

@register
def llm_detect_intent():
    print("Detecting intent using LLM...")