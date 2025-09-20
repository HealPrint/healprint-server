import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't exist
try:
    load_dotenv()
    print("✅ .env file loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load .env file: {e}")
    print("Using default values and system environment variables")

# OpenAI/OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SITE_URL = os.getenv("SITE_URL", "https://healprint.xyz")
SITE_NAME = os.getenv("SITE_NAME", "HealPrint AI")

# Chat Configuration
MAX_CONVERSATION_LENGTH = int(os.getenv("MAX_CONVERSATION_LENGTH", "50"))
DIAGNOSTIC_THRESHOLD = float(os.getenv("DIAGNOSTIC_THRESHOLD", "0.7"))

# Debug: Print loaded configuration
print(f"🔧 Configuration loaded:")
print(f"   SITE_URL: {SITE_URL}")
print(f"   SITE_NAME: {SITE_NAME}")
print(f"   MAX_CONVERSATION_LENGTH: {MAX_CONVERSATION_LENGTH}")
print(f"   DIAGNOSTIC_THRESHOLD: {DIAGNOSTIC_THRESHOLD}")
print(f"   OPENROUTER_API_KEY: {'***' if OPENROUTER_API_KEY else 'Not set'}")
