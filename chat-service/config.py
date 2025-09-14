import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI/OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SITE_URL = os.getenv("SITE_URL", "https://healprint.xyz")
SITE_NAME = os.getenv("SITE_NAME", "HealPrint AI")

# Chat Configuration
MAX_CONVERSATION_LENGTH = 50
DIAGNOSTIC_THRESHOLD = 0.7
