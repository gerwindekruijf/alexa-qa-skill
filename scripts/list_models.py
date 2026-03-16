from google import genai

from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

print("Listing available models...")

# In the NEW SDK, we iterate directly
for m in client.models.list():
    print(f"- {m.name}")
    # Optional: Print supported actions if available to verify 'generateContent'
    if hasattr(m, 'supported_actions'):
        print(f"  Actions: {m.supported_actions}")
