import requests
import os
import json

def handle_labs(update=None, context=None):
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:42002')
    api_key = os.getenv('API_KEY', 'my-secret-api-key')
    
    try:
        response = requests.get(
            f"{backend_url}/items/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        
        if response.status_code == 200:
            try:
                items = response.json()
                labs = [item for item in items if item.get('type') == 'lab']
                
                if labs:
                    lab_list = "\n".join([f"- {lab['title']}" for lab in labs])
                    return f"Available labs:\n{lab_list}"
                else:
                    return "No labs found"
            except json.JSONDecodeError:
                return f"Backend error: Invalid JSON response"
        else:
            return f"Backend error: HTTP {response.status_code}"
    except Exception as e:
        return f"Backend error: {str(e)}"
