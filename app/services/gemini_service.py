import re

from google import genai
from google.genai.types import GenerateContentConfig

from app.config import GEMINI_API_KEY


class GeminiService:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-3.1-flash-lite-preview"

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.2) -> str:
        config = GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=(
                "Je bent een Q&A AI assistent voor Alexa. "
                "Geef een zo goed mogelijk antwoord op basis van de gestelde vraag. "
                "Gebruik geen HTML of Markdown, alleen platte tekst. "
                "Wees beknopt en to the point, maar zorg dat je antwoord volledig is. "
            ),
        )

        response = self.gemini_client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=config
        )

        raw_text = getattr(response, "text", "")
        return self._post_process(raw_text)

    def _post_process(self, text: str, max_length: int = 2000) -> str:
        # Alexa max length = 8000 chars, for nice output 2000 is enough
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_length]
