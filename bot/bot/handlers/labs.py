import requests
import os

def handle_labs(update, context):
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:42002')
    api_key = os.getenv('API_KEY')
    
    try:
        response = requests.get(
            f"{backend_url}/api/labs",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        if response.status_code == 200:
            labs = response.json()
            lab_list = "\n".join([f"- {lab['name']}" for lab in labs])
            return f"Available labs:\n{lab_list}"
        else:
            return "Unable to fetch labs at this time."
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"
