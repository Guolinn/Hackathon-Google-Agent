from __future__ import annotations

import json
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import Settings


class CrisisFlowAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_text(self, prompt: str) -> str | None:
        if not self.settings.use_gemini:
            return None

        return self._generate_with_rest(prompt) or self._generate_with_sdk(prompt)

    def _generate_with_rest(self, prompt: str) -> str | None:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ]
        }
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.settings.gemini_api_key or "",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=20, context=self._ssl_context()) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            return None

        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def _ssl_context() -> ssl.SSLContext:
        try:
            import certifi

            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            return ssl.create_default_context()

    def _generate_with_sdk(self, prompt: str) -> str | None:
        try:
            from google import genai
        except Exception:
            return None

        try:
            client = genai.Client(api_key=self.settings.gemini_api_key)
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
            )
            return getattr(response, "text", None)
        except Exception:
            return None
