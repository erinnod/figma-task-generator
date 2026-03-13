from openai import OpenAI
from src.config import settings
from src.llm.prompts import SYSTEM_PROMPT


class LLMClientError(Exception):
    pass


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self._client = self._initialise_client()

    def _initialise_client(self):
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise LLMClientError(
                    "OPENAI_API_KEY is not set in your .env file."
                )
            return OpenAI(api_key=settings.openai_api_key)
        raise LLMClientError(
            f"Unsupported LLM provider: {self.provider}"
        )

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        """
        Send a prompt and return the text response.
        Accepts an optional system prompt override.
        """
        try:
            if self.provider == "openai":
                return self._complete_openai(prompt, system_prompt)
        except Exception as e:
            raise LLMClientError(f"LLM call failed: {e}")

    def _complete_openai(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        system = system_prompt if system_prompt else SYSTEM_PROMPT
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content