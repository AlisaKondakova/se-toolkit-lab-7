#!/usr/bin/env python3
"""Main entry point for SE Toolkit Bot."""

import argparse
import asyncio
import sys
import logging
from typing import Optional

from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

from config import BotConfig
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
)


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Test mode handlers (sync versions for CLI)
def test_start(args: str) -> str:
    """Wrapper for test mode."""
    return handle_start(args)


def test_help(args: str) -> str:
    """Wrapper for test mode."""
    return handle_help(args)


def test_health(args: str) -> str:
    """Wrapper for test mode (async handler in test mode)."""
    # For now, return placeholder
    # In production, this would need to be async
    return "🟡 Health check (use Telegram for async version)"


def test_labs(args: str) -> str:
    """Wrapper for test mode."""
    return "📋 Labs listing (placeholder)"


# Telegram handlers (async versions)
async def telegram_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command in Telegram."""
    response = handle_start("")
    await update.message.reply_text(response)


async def telegram_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command in Telegram."""
    response = handle_help("")
    await update.message.reply_text(response)


async def telegram_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command in Telegram."""
    # TODO: Implement async health check
    response = "🟢 Backend is healthy (implementation coming in Task 2)"
    await update.message.reply_text(response)


async def telegram_labs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /labs command in Telegram."""
    # TODO: Implement async labs listing
    response = "📋 Available labs (implementation coming in Task 2)"
    await update.message.reply_text(response)


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in Telegram bot."""
    logger.error(f"Exception while handling update {update}: {context.error}")


def run_telegram_bot():
    """Run the bot in Telegram mode."""
    config = BotConfig.from_env()
    
    if not config.bot_token:
        logger.error("BOT_TOKEN not set in environment")
        sys.exit(1)
    
    # Create application
    app = Application.builder().token(config.bot_token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", telegram_start))
    app.add_handler(CommandHandler("help", telegram_help))
    app.add_handler(CommandHandler("health", telegram_health))
    app.add_handler(CommandHandler("labs", telegram_labs))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def run_test_mode(command: str):
    """Run bot in test mode."""
    # Parse command and arguments
    parts = command.strip().split()
    cmd = parts[0] if parts else ""
    args = " ".join(parts[1:]) if len(parts) > 1 else ""
    
    # Route to appropriate handler
    handlers = {
        "/start": test_start,
        "/help": test_help,
        "/health": test_health,
        "/labs": test_labs,
    }
    
    if cmd in handlers:
        try:
            response = handlers[cmd](args)
            print(response)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}")
        print("Available test commands: /start, /help, /health, /labs")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SE Toolkit Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Run in test mode with command (e.g., --test '/start')",
    )
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_bot()


if __name__ == "__main__":
    main()
