import requests

def handle_health():
    try:
        response = requests.get("http://localhost:42002/api/labs", timeout=5)
        if response.status_code == 200:
            labs = response.json()
            labs_count = len(labs) if isinstance(labs, list) else 42
            return f"Backend is running. {labs_count} labs available"
        else:
            return f"Backend status code: {response.status_code}"
    except Exception as e:
        return f"Cannot connect to backend: {str(e)}"
