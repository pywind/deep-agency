import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

# LinkedIn credentials
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Server settings
PORT = int(os.getenv("PORT", "8001"))
HOST = os.getenv("HOST", "0.0.0.0")

# LangGraph settings
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0

# Application settings
MAX_POSTS_TO_ANALYZE = 5 