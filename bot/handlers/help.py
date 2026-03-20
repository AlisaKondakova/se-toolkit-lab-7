def handle_help(update, context):
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List all available labs
/scores <lab> - Show pass rates for a specific lab (e.g., /scores lab-04)"""
