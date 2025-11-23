from registry import register

@register
def validate_order_id():
    print("Validating order ID...")

@register
def fetch_order_status():
    print("Fetching order status...")