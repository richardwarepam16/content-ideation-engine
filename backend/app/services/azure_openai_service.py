from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-02-15-preview",
        )
        self.deployment = os.getenv("AZURE_DEPLOYMENT")

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "You are a helpful expert assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Azure OpenAI returned empty content")

        return content