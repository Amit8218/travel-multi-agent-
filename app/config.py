import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv(), override=True)

APP_NAME = os.getenv("APP_NAME", "AI Travel Guide Agent")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
_enabled_str = os.getenv("LANGFUSE_ENABLED", "false").lower()
LANGFUSE_ENABLED = _enabled_str in ("true", "1", "yes")

# Tracing is only truly enabled if host and both keys are configured
if LANGFUSE_ENABLED and (not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY):
    LANGFUSE_ENABLED = False

_show_progress_str = os.getenv("SHOW_AGENT_PROGRESS", "false").lower()
SHOW_AGENT_PROGRESS = _show_progress_str in ("true", "1", "yes")


def validate_config() -> list[str]:
    """
    Returns a list of missing critical environment variables.
    """
    missing = []
    if not OPENROUTER_API_KEY:
        missing.append("OPENROUTER_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if not OPENWEATHER_API_KEY:
        missing.append("OPENWEATHER_API_KEY")
    return missing
