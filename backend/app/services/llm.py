
from backend.app.dependencies.resources import resources


class LLMService:
    def __init__(self):
        self.settings = resources.settings
        self.client = None

    def _get_client(self):
        if self.client is None:
            if not self.settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not configured.")

            from groq import Groq

            self.client = Groq(
                api_key=self.settings.GROQ_API_KEY,
                timeout=self.settings.GROQ_TIMEOUT,
                max_retries=self.settings.GROQ_MAX_RETRIES,
            )

            print("Groq LLM initialized.")

        return self.client

    def generate_response(self, question: str) -> str:
        client = self._get_client()

        completion = client.chat.completions.create(
            model=self.settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": self.settings.LLM_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0.3,
        )

        return completion.choices[0].message.content
