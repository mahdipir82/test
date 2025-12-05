import requests

PRODUCT_API = "http://127.0.0.1:8000/products/api/list/"

def fetch_products():
    try:
        response = requests.get(PRODUCT_API)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []
