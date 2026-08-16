from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    provider_name = "base"

    @abstractmethod
    def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        raise NotImplementedError


class GroqProvider(AIProvider):
    provider_name = "groq"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is required for Groq provider access.")

        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("The groq package is not installed. Install it with `pip install groq`.") from exc

        client = Groq(api_key=self.api_key)
        content = context or ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a research assistant that distinguishes retrieved evidence from model-generated reasoning."},
                {"role": "user", "content": f"Context:\n{content}\n\nPrompt:\n{prompt}"},
            ],
        )
        return completion.choices[0].message.content
