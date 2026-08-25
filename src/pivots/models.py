"""Model wrapper.

Anything that speaks the OpenAI chat-completions protocol works: the OpenAI API,
a Gemini-compatible proxy, vLLM, or Ollama. Point --base-url at it.
"""

from __future__ import annotations

import os
import time


class ChatModel:
    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
        timeout: float = 180.0,
    ) -> None:
        from openai import OpenAI  # lazy import

        self.model = model
        self.max_retries = max_retries
        self.client = OpenAI(
            base_url=base_url or os.environ.get("PIVOTS_BASE_URL") or None,
            api_key=api_key or os.environ.get("PIVOTS_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            timeout=timeout,
        )

    def complete(self, messages: list[dict]) -> str:
        """Run one request. No sampling parameters are set: the paper uses each
        provider's default configuration."""
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages
                )
                return response.choices[0].message.content or ""
            except Exception as exc:  # noqa: BLE001 - surfaced after retries
                last_error = exc
                time.sleep(2**attempt)
        raise RuntimeError(f"model call failed after {self.max_retries} attempts") from last_error
