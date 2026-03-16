import os

from dotenv import load_dotenv

load_dotenv()

# Auth
# AUTH_SECRET = os.environ["AUTH_SECRET"]

# Alexa
ALEXA_SKILL_ID = os.environ["ALEXA_SKILL_ID"]
ALEXA_NAME = "Mini Link"

# Gemini
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
