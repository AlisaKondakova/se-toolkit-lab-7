import httpx
import os

def handle_scores(update, context, lab_name):
    if not lab_name:
        return "❌ Please specify a lab. Example: /scores lab-04"
    
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:42002')
    api_key = os.getenv('BACKEND_API_KEY', '')
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{backend_url}/analytics/pass-rates",
                params={"lab": lab_name},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Проверяем тип данных
            if isinstance(data, list):
                if not data:
                    return f"No pass rate data found for {lab_name}"
                # Если список, форматируем каждый элемент
                result = f"Pass rates for {lab_name}:\n"
                for item in data:
                    task_name = item.get('task', item.get('name', 'Unknown'))
                    rate = item.get('pass_rate', item.get('rate', 0))
                    attempts = item.get('attempts', '')
                    if attempts:
                        result += f"- {task_name}: {rate}% ({attempts} attempts)\n"
                    else:
                        result += f"- {task_name}: {rate}%\n"
                return result
            elif isinstance(data, dict):
                if not data:
                    return f"No pass rate data found for {lab_name}"
                result = f"Pass rates for {lab_name}:\n"
                for task_name, rate in data.items():
                    result += f"- {task_name}: {rate}%\n"
                return result
            else:
                return f"Unexpected data format for {lab_name}"
                
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab '{lab_name}' not found. Use /labs to see available labs."
        return f"❌ Backend error: HTTP {e.response.status_code}"
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({backend_url}). Check that the services are running."
    except Exception as e:
        return f"❌ Backend error: {str(e)}"
