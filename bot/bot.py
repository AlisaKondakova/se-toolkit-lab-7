#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores

def handle_command(cmd):
    parts = cmd.strip().split()
    if not parts:
        return "No command provided"
    
    command = parts[0]
    
    if command == "/start":
        return handle_start(None, None)
    elif command == "/help":
        return handle_help(None, None)
    elif command == "/health":
        return handle_health(None, None)
    elif command == "/labs":
        return handle_labs(None, None)
    elif command == "/scores":
        lab_name = parts[1] if len(parts) > 1 else None
        return handle_scores(None, None, lab_name)
    else:
        return f"Unknown command: {command}\nUse /help to see available commands."

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        cmd = sys.argv[2] if len(sys.argv) > 2 else "/start"
        result = handle_command(cmd)
        print(result)
        sys.exit(0)
    else:
        print("Bot running...")
