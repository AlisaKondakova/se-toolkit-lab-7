"""Configuration management for the bot."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Bot configuration from environment variables."""
    
    # Required fields first (no defaults)
    lms_api_url: str
    lms_api_key: str
    
    # Optional fields with defaults
    bot_token: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_api_url: str = "http://localhost:42005"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """Load configuration from environment variables."""
        return cls(
            lms_api_url=os.getenv("LMS_API_URL", "http://localhost:42002"),
            lms_api_key=os.getenv("LMS_API_KEY", ""),
            bot_token=os.getenv("BOT_TOKEN"),
            llm_api_key=os.getenv("LLM_API_KEY"),
            llm_api_url=os.getenv("LLM_API_URL", "http://localhost:42005"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
