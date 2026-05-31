"""
Neuro Router - Model routing with key pooling
Uses official provider SDKs / OpenAI-compatible SDKs where providers expose them.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

from neuro.models import MODEL_ROLES

GOOGLE_PROVIDER = "google"
UNKNOWN_MODEL_CHAIN = [
    "groq/llama-3.3-70b-versatile",
    "gemini-2.5-flash",
    "openrouter/openrouter/free",
]


# =============================================================================
# KEY MANAGEMENT
# =============================================================================

def _get_env_keys(var_name: str) -> List[str]:
    """Get API keys from environment (supports comma-separated)."""
    value = os.getenv(var_name, "")
    if not value:
        return []
    return [k.strip() for k in value.split(",") if k.strip()]


def _get_key_pool(plural: str, singular: str) -> List[str]:
    keys = _get_env_keys(plural)
    if keys:
        return keys
    key = os.getenv(singular, "")
    return [key.strip()] if key.strip() else []


# Load keys from environment. Native Google Gemini uses GEMINI_* for compatibility
# plus GOOGLE_* for explicit provider naming.
GOOGLE_KEYS = (
    _get_key_pool("GEMINI_API_KEYS", "GEMINI_API_KEY")
    or _get_key_pool("GOOGLE_API_KEYS", "GOOGLE_API_KEY")
)
GROQ_KEYS = _get_key_pool("GROQ_API_KEYS", "GROQ_API_KEY")
OPENROUTER_KEYS = _get_key_pool("OPENROUTER_API_KEYS", "OPENROUTER_API_KEY")

# Backward-compatible alias for callers that import GEMINI_KEYS directly.
GEMINI_KEYS = GOOGLE_KEYS


def _normalize_provider(provider: str) -> str:
    aliases = {"gemini": GOOGLE_PROVIDER, "google": GOOGLE_PROVIDER}
    return aliases.get(provider, provider)


def _split_model(model: str) -> Tuple[str, str]:
    """Split provider-aware model strings while preserving native Gemini IDs."""
    if model.startswith("google/"):
        return GOOGLE_PROVIDER, model.split("/", 1)[1]
    if model.startswith("gemini-"):
        return GOOGLE_PROVIDER, model
    if "/" in model:
        provider, model_name = model.split("/", 1)
        return _normalize_provider(provider), model_name
    return "openrouter", model


def validate_keys(require_any: bool = False) -> Dict[str, bool]:
    """Validate provider key availability without failing imports by default."""
    providers = {
        GOOGLE_PROVIDER: bool(GOOGLE_KEYS),
        "groq": bool(GROQ_KEYS),
        "openrouter": bool(OPENROUTER_KEYS),
    }
    if require_any and not any(providers.values()):
        raise RuntimeError(
            "No API keys found! Set at least one of:\n"
            "  - GEMINI_API_KEY or GOOGLE_API_KEY\n"
            "  - GROQ_API_KEY\n"
            "  - OPENROUTER_API_KEY"
        )
    return providers


# =============================================================================
# ROUTER
# =============================================================================

class NeuroRouter:
    """Neuro model router with key rotation."""

    def __init__(self) -> None:
        self.key_index = {GOOGLE_PROVIDER: 0, "groq": 0, "openrouter": 0}
        self.cooldowns: dict[str, float] = {}

    def get_key(self, provider: str) -> Optional[str]:
        """Get next available key for provider."""
        provider = _normalize_provider(provider)
        if provider == GOOGLE_PROVIDER:
            keys = GOOGLE_KEYS
        elif provider == "groq":
            keys = GROQ_KEYS
        elif provider == "openrouter":
            keys = OPENROUTER_KEYS
        else:
            return None

        if not keys:
            return None

        for _ in range(len(keys)):
            idx = self.key_index[provider] % len(keys)
            self.key_index[provider] += 1
            key = keys[idx]

            cooldown_key = f"{provider}:{idx}"
            if cooldown_key in self.cooldowns and time.time() - self.cooldowns[cooldown_key] < 60:
                continue

            return key

        return None

    def mark_rate_limited(self, provider: str, idx: int) -> None:
        """Mark a key as rate limited."""
        provider = _normalize_provider(provider)
        self.cooldowns[f"{provider}:{idx}"] = time.time()


# Global router instance
_router = NeuroRouter()


# =============================================================================
# MODEL CALLS
# =============================================================================

def complete(role: str, messages: List[dict], model: Optional[str] = None, **kwargs: Any) -> str:
    """Call a model through Neuro router."""
    if model:
        provider, model_name = _split_model(model)
    elif role in MODEL_ROLES:
        provider, model_name = _split_model(MODEL_ROLES[role]["primary"])
    else:
        provider, model_name = _split_model(UNKNOWN_MODEL_CHAIN[0])

    api_key = _router.get_key(provider)
    if not api_key:
        raise RuntimeError(f"No API key for {provider}")

    try:
        if provider == GOOGLE_PROVIDER:
            return _call_google(model_name, messages, api_key, **kwargs)
        if provider == "groq":
            return _call_groq(model_name, messages, api_key, **kwargs)
        if provider == "openrouter":
            return _call_openrouter(model_name, messages, api_key, **kwargs)
        raise RuntimeError(f"Unsupported provider: {provider}")
    except Exception as e:
        raise RuntimeError(f"Model call failed: {e}") from e


def _call_google(model: str, messages: list, api_key: str, **kwargs: Any) -> str:
    """Call native Google Gemini with the official google-genai SDK."""
    try:
        import google.genai as genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("google-genai not installed: pip install google-genai") from exc

    client = genai.Client(api_key=api_key)
    contents = []
    for msg in messages:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg.get("content", ""))]))

    clean_kwargs = {k: v for k, v in kwargs.items() if k in {"temperature", "max_output_tokens", "top_p", "stop"}}
    if "max_tokens" in kwargs and "max_output_tokens" not in clean_kwargs:
        clean_kwargs["max_output_tokens"] = kwargs["max_tokens"]

    response = client.models.generate_content(model=model, contents=contents, **clean_kwargs)
    return response.text or ""


# Backward-compatible alias.
def _call_gemini(model: str, messages: list, api_key: str, **kwargs: Any) -> str:
    return _call_google(model, messages, api_key, **kwargs)


def _call_groq(model: str, messages: list, api_key: str, **kwargs: Any) -> str:
    """Call Groq using the official Groq SDK."""
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("groq not installed: pip install groq") from exc

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content or ""


def _call_openrouter(model: str, messages: list, api_key: str, **kwargs: Any) -> str:
    """Call OpenRouter via its OpenAI-compatible API using the official OpenAI SDK."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai not installed: pip install openai") from exc

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content or ""


# =============================================================================
# UTILITIES
# =============================================================================

def has_provider(provider: str) -> bool:
    """Check if provider has keys."""
    provider = _normalize_provider(provider)
    return bool(available_providers().get(provider, 0))


def available_providers() -> Dict[str, int]:
    """Get provider key counts."""
    return {
        GOOGLE_PROVIDER: len(GOOGLE_KEYS),
        "groq": len(GROQ_KEYS),
        "openrouter": len(OPENROUTER_KEYS),
    }
