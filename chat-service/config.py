import os
from dotenv import load_dotenv
from pathlib import Path

# Try to load .env file, but don't fail if it doesn't exist
try:
    # Load .env placed next to this config file, regardless of current working directory
    env_path = Path(__file__).with_name('.env')
    load_dotenv(dotenv_path=env_path)
    print(" .env file loaded successfully")
except Exception as e:
    print(f"  Warning: Could not load .env file: {e}")
    print("Using default values and system environment variables")

# OpenAI/OpenRouter Configuration
# Uses environment variable if set (and non-empty); otherwise falls back to provided key
OPENROUTER_API_KEY = (os.getenv("OPENROUTER_API_KEY") or 
    "").strip()
SITE_URL = os.getenv("SITE_URL", "https://healprint.xyz")
SITE_NAME = os.getenv("SITE_NAME", "HealPrint AI")

# Chat Configuration
MAX_CONVERSATION_LENGTH = int(os.getenv("MAX_CONVERSATION_LENGTH", "50"))
DIAGNOSTIC_THRESHOLD = float(os.getenv("DIAGNOSTIC_THRESHOLD", "0.7"))

REDIS_URL = os.getenv("REDIS_URL")

# Debug: minimal masked config print
try:
    masked_key = (OPENROUTER_API_KEY[:6] + "..." + OPENROUTER_API_KEY[-4:]) if OPENROUTER_API_KEY else "Not set"
    print(f"Config: SITE_URL={SITE_URL} | CHAT MAX_LEN={MAX_CONVERSATION_LENGTH} | DIAG_THR={DIAGNOSTIC_THRESHOLD} | OPENROUTER_API_KEY={masked_key}")
except Exception:
    pass
