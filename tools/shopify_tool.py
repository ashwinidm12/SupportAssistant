# tools/shopify_tool.py
import os, requests

SHOP_NAME = os.environ.get("SHOPIFY_SHOP_NAME")
SHOP_API_KEY = os.environ.get("SHOPIFY_API_KEY")
SHOP_PASSWORD = os.environ.get("SHOPIFY_PASSWORD_OR_ACCESS_TOKEN")

def get_order(order_id):
    if not SHOP_NAME or not SHOP_API_KEY:
        return None
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2025-01/orders.json?name={order_id}"
    resp = requests.get(url, auth=(SHOP_API_KEY, SHOP_PASSWORD))
    if resp.status_code == 200:
        data = resp.json()
        if data.get("orders"):
            return data["orders"][0]
    return None
