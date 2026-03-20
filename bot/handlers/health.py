"""Handler for /health command."""

import httpx


async def handle_health(args: str = "") -> str:
    """Check backend health.
    
    Args:
        args: Command arguments (ignored for health)
        
    Returns:
        Health status message
    """
    # TODO: Implement real health check in Task 2
    # For now, return placeholder
    return "🟡 Health check endpoint (coming in Task 2)\nBackend will be checked at: http://localhost:42002/health"
