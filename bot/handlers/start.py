"""Handler for /start command."""


def handle_start(args: str = "") -> str:
    """Handle /start command.
    
    Args:
        args: Command arguments (ignored for start)
        
    Returns:
        Welcome message
    """
    return (
        "🎯 Welcome to SE Toolkit Lab Bot!\n\n"
        "I help you manage your lab assignments and track your progress.\n\n"
        "Available commands:\n"
        "/help - Show all commands\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores [lab] - Get your scores for a lab\n\n"
        "You can also ask me questions in natural language!"
    )
