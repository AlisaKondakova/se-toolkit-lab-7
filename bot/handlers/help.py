"""Handler for /help command."""


def handle_help(args: str = "") -> str:
    """Handle /help command.
    
    Args:
        args: Command arguments (ignored for help)
        
    Returns:
        Help message with available commands
    """
    return (
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend API status\n"
        "/labs - List all available labs\n"
        "/scores [lab] - Get your scores (e.g., /scores lab-04)\n\n"
        "💡 You can also ask:\n"
        "- 'What labs are available?'\n"
        "- 'Show my scores for lab-04'\n"
        "- 'What's my progress?'\n\n"
        "🔧 Development mode - real implementation coming in Task 2!"
    )
