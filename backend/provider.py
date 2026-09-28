"""
Scam Shield - LLM Provider Module
Abstract provider interface with Google Gemini implementation.
Allows seamless model swapping (e.g. gemini-3.8-flash, gemini-2.5-flash, or custom).
"""

from __future__ import annotations
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from google import genai
from google.genai import types

logger = logging.getLogger("scam_shield.provider")


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured and available to make requests."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str) -> str:
        """Generates text from a prompt and system instruction."""
        pass

    @abstractmethod
    def generate_vision(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system_instruction: str
    ) -> str:
        """Performs multimodal analysis on an image (e.g. screenshot) and prompt."""
        pass


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini API implementation using the modern `google-genai` SDK.
    Supports gemini-3.8-flash (recommended) or configurable via GEMINI_MODEL.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        # Default to current Gemini standard model, allowing override
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self._client: Optional[genai.Client] = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")
                self._client = None

    def is_available(self) -> bool:
        return bool(self._client and self.api_key)

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        if not self.is_available() or not self._client:
            raise RuntimeError("Gemini Provider is not configured or missing GEMINI_API_KEY.")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1,  # Low temperature for deterministic classification
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=[prompt],
            config=config,
        )

        if not response.text:
            raise ValueError("Gemini returned empty response text.")
        return response.text.strip()

    def generate_vision(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        system_instruction: str
    ) -> str:
        if not self.is_available() or not self._client:
            raise RuntimeError("Gemini Provider is not configured or missing GEMINI_API_KEY.")

        part_image = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1,
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=[prompt, part_image],
            config=config,
        )

        if not response.text:
            raise ValueError("Gemini Vision returned empty response text.")
        return response.text.strip()


# Global singleton provider instance
_provider: Optional[BaseLLMProvider] = None


def get_llm_provider() -> BaseLLMProvider:
    """Returns the configured LLM provider instance."""
    global _provider
    if _provider is None:
        _provider = GeminiProvider()
    return _provider


def set_llm_provider(custom_provider: BaseLLMProvider) -> None:
    """Allows injecting custom or mock providers for testing."""
    global _provider
    _provider = custom_provider
