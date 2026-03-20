import httpx
import os

def handle_labs(update, context):
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:42002')
    api_key = os.getenv('BACKEND_API_KEY', '')
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{backend_url}/items/",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0
            )
            response.raise_for_status()
            items = response.json()
            
            # Фильтруем лабы
            labs = [item for item in items if item.get('type') == 'lab']
            
            if not labs:
                return "No labs found."
            
            result = "Available labs:\n"
            for lab in labs:
                name = lab.get('name', lab.get('id', 'Unknown'))
                result += f"- {name}\n"
            return result
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
