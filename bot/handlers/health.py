import httpx
import os

def handle_health(update, context):
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
            return f"✅ Backend is healthy. {len(items)} items available."
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({backend_url}). Check that the services are running."
    except httpx.TimeoutException:
        return f"❌ Backend error: timeout ({backend_url}). The service is not responding."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
