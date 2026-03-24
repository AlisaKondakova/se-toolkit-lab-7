import re
import requests
import logging

logger = logging.getLogger(__name__)

class IntentRouter:
    def __init__(self, backend_url, api_key):
        self.backend_url = backend_url
        self.api_key = api_key
    
    def _make_request(self, endpoint, params=None):
        """Make API request to backend"""
        url = f"{self.backend_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            if params:
                response = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            logger.error(f"API error {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def _format_labs(self, items):
        """Format labs list"""
        labs = [item for item in items if item.get('type') == 'lab']
        if not labs:
            return "No labs found."
        result = "📚 *Available Labs:*\n\n"
        for lab in labs:
            lab_id = lab.get('id', '')
            lab_name = lab.get('name', lab.get('title', f'Lab {lab_id}'))
            result += f"• **{lab_id}** — {lab_name}\n"
        return result
    
    def route(self, message):
        """Route user message to appropriate action"""
        message_lower = message.lower()
        
        # Greeting
        if re.search(r'\b(hi|hello|hey|greetings|hi there)\b', message_lower):
            return "👋 Hello! I'm your Lab Analytics Assistant!"
        
        # Help
        if re.search(r'\b(help|what can you do)\b', message_lower):
            return "I can help with labs, scores, pass rates, and top learners."
        
        # List labs
        if re.search(r'(what|which).*(labs|tasks|available)', message_lower):
            data = self._make_request("/items/")
            if data:
                return self._format_labs(data)
            return "Unable to fetch labs."
        
        # Get pass rates
        lab_match = re.search(r'lab[- ]?(\d+)', message_lower)
        if lab_match:
            lab_num = lab_match.group(1).zfill(2)
            lab_id = f"lab-{lab_num}"
            
            if re.search(r'(score|pass|rate)', message_lower):
                data = self._make_request("/analytics/pass-rates", params={"lab": lab_id})
                if data:
                    result = f"📊 *{lab_id} - Pass Rates*\n\n"
                    for task in data:
                        task_name = task.get('task', 'Task')
                        pass_rate = task.get('pass_rate', 0)
                        attempts = task.get('attempts', 0)
                        result += f"• {task_name}: {pass_rate:.1f}% ({attempts} attempts)\n"
                    return result
                return f"No data for {lab_id}"
        
        # Which lab has lowest pass rate?
        if re.search(r'(lowest|worst).*(pass|rate)', message_lower):
            items = self._make_request("/items/")
            if items:
                labs = [item for item in items if item.get('type') == 'lab']
                results = []
                for lab in labs:
                    lab_id = lab.get('id')
                    data = self._make_request("/analytics/pass-rates", params={"lab": lab_id})
                    if data and len(data) > 0:
                        avg_rate = sum(t.get('pass_rate', 0) for t in data) / len(data)
                        results.append((lab_id, avg_rate))
                if results:
                    results.sort(key=lambda x: x[1])
                    return f"Lowest pass rate: {results[0][0]} at {results[0][1]:.1f}%"
            return "Unable to compare pass rates."
        
        return "Try: 'what labs are available?' or 'show me scores for lab 04'"
