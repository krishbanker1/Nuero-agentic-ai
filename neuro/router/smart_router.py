"""
Smart Router - Rotating provider with circuit breaker
Now with skill middleware integration and improved reliability
"""

import os
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import threading

GOOGLE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-embedding-2",
]

# OpenRouter models - ONLY truly FREE models NOT on Groq or Gemini
# Verified free on OpenRouter June 2026
OPENROUTER_UNIQUE_MODELS = [
    "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
]

UNKNOWN_TASK_MODEL_CHAIN = [
    "groq/llama-3.3-70b-versatile",
    "gemini-3.5-flash",
    "qwen/qwen3-coder:free",
]

# Import skill middleware
try:
    from neuro.skills.skill_middleware import get_middleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False

# =============================================================================
# PROVIDER ENUM - ALL SUPPORTED PROVIDERS
# =============================================================================

class Provider(Enum):
    """Available API providers - FREE TIER ONLY.

    CONFIRMED FREE:
    - Gemini (Google): 15 RPM, generous quota
    - Groq: Very generous free tier, fast inference
    - OpenRouter: 100+ :free models (deepseek, qwen, llama, etc)
    - Cloudflare: Workers AI free tier
    - HuggingFace: Inference API free tier

    REQUIRES PAID (added but will fail without key):
    - Mistral, Cohere, Perplexity, DeepSeek, Together
    """
    GOOGLE = "google"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"
    CLOUDFLARE = "cloudflare"
    TOGETHER = "together"
    MISTRAL = "mistral"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"
    DEEPSEEK = "deepseek"


# =============================================================================
# KEY MANAGEMENT - Generic format for all providers
# Format: {PROVIDER}_API_KEYS (comma-separated for multiple keys)
# Fallback: {PROVIDER}_API_KEY (singular)
# =============================================================================

def _get_env_keys_for_provider(provider: Provider) -> List[str]:
    """
    Get API keys from environment for any provider using generic format.
    Supports comma-separated values: key1,key2,key3
    """
    env_names = []
    if provider == Provider.GOOGLE:
        # Native Google Gemini keeps historic GEMINI_* plus official GOOGLE_* env vars.
        env_names.extend([("GEMINI_API_KEYS", "GEMINI_API_KEY"), ("GOOGLE_API_KEYS", "GOOGLE_API_KEY")])
    else:
        env_names.append((f"{provider.name.upper()}_API_KEYS", f"{provider.name.upper()}_API_KEY"))

    for env_plural, env_singular in env_names:
        value = os.getenv(env_plural, "")
        if value:
            keys = [k.strip() for k in value.split(",") if k.strip()]
            if keys:
                return keys

        singular = os.getenv(env_singular, "")
        if singular:
            return [singular.strip()]

    return []

# Legacy helper for backwards compatibility
def _get_env_keys(var_name: str, fallback_singular: str = None) -> List[str]:
    """Get API keys from environment (supports comma-separated)."""
    value = os.getenv(var_name, "")
    if value:
        keys = [k.strip() for k in value.split(",") if k.strip()]
        if keys:
            return keys

    if fallback_singular:
        singular = os.getenv(fallback_singular, "")
        if singular:
            return [singular.strip()]

    return []

def _init_provider_keys() -> Dict[str, List[str]]:
    """Initialize API keys for all providers using generic format."""
    return {
        # Use generic format: {PROVIDER}_API_KEYS
        provider.value: _get_env_keys_for_provider(provider)
        for provider in Provider
    }


# Initialize keys at module load
_PROVIDER_KEYS = _init_provider_keys()


def _normalize_provider_name(provider: str) -> str:
    """Normalize legacy provider aliases to canonical provider names."""
    aliases = {"gemini": "google", "google": "google"}
    return aliases.get(provider, provider)


def get_provider_keys(provider: str) -> List[str]:
    """Get API keys for a provider."""
    return _PROVIDER_KEYS.get(_normalize_provider_name(provider), [])


def has_provider(provider: str) -> bool:
    """Check if provider has available keys."""
    return bool(get_provider_keys(provider))


def available_providers() -> Dict[str, int]:
    """Get provider key counts, including zero-count providers for health checks."""
    return {provider: len(keys) for provider, keys in _PROVIDER_KEYS.items()}


def reload_keys():
    """Reload keys from environment (useful for testing)."""
    global _PROVIDER_KEYS
    _PROVIDER_KEYS = _init_provider_keys()


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: Provider
    base_url: str
    api_key_env: str
    models: List[str]
    requires_endpoint: bool = False
    rate_limit: int = 60  # requests per minute
    cooldown: int = 60  # seconds after rate limit


@dataclass
class RouterStats:
    """Statistics for routing decisions."""
    total_calls: int = 0
    provider_calls: Dict[str, int] = field(default_factory=dict)
    failures: Dict[str, int] = field(default_factory=dict)
    avg_latency: Dict[str, float] = field(default_factory=dict)
    last_used: Dict[str, float] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)
    # Circuit breaker state
    failures_since_success: Dict[str, int] = field(default_factory=dict)
    circuit_open_until: Dict[str, float] = field(default_factory=dict)


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 3   # Open circuit after N failures
    recovery_timeout: int = 30  # Seconds before trying again
    half_open_max_calls: int = 1  # Max calls in half-open state


class SmartRouter:
    """
    Intelligent router that rotates across multiple FREE API providers.
    Ensures best model selection and automatic failover.
    NOW WITH SKILL MIDDLEWARE INTEGRATION for 259+ skills.
    Supports 50+ free models with 22 task categories.
    """

    # Provider configurations with 50+ models
    PROVIDERS: Dict[Provider, ProviderConfig] = {
        Provider.GOOGLE: ProviderConfig(
            name=Provider.GOOGLE,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key_env="GEMINI_API_KEYS",
            models=GOOGLE_MODELS,
            rate_limit=60,
        ),
        Provider.GROQ: ProviderConfig(
            name=Provider.GROQ,
            base_url="https://api.groq.com/openai/v1",
            api_key_env="GROQ_API_KEYS",
            models=[
                # GPT-OSS models - Best reasoning
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                # Qwen - Coding specialized
                "qwen/qwen3-32b",
                # Llama - Fast versatile
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                # Groq Compound - Agentic with tools
                "groq/compound",
                "groq/compound-mini",
            ],
            rate_limit=30,
        ),
        Provider.OPENROUTER: ProviderConfig(
            name=Provider.OPENROUTER,
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEYS",
            models=[
                # DeepSeek - fast flash variant
                "nvidia/nemotron-3-super-120b-a12b:free",
                # Qwen models - specialized coders
                "qwen/qwen3-coder:free",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                # Google Gemma - fast reasoning
                "google/gemma-4-31b-it:free",
                "google/gemma-4-26b-a4b-it:free",
                # Meta Llama - versatile
                "meta-llama/llama-3.3-70b-instruct:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                # NVIDIA Nemotron - 120B reasoning
                "nvidia/nemotron-3-super-120b-a12b:free",
                "nvidia/nemotron-nano-9b-v2:free",
                # Mistral - Dolphin variant
                "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            ],
            rate_limit=60,
        ),
        Provider.HUGGINGFACE: ProviderConfig(
            name=Provider.HUGGINGFACE,
            base_url="https://api-inference.huggingface.co/models",
            api_key_env="HF_TOKEN",
            models=[
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "deepseek-ai/DeepSeek-Coder-V2",
                "bigcode/CodeLlama-70B-Instruct",
                "bigcode/Starcoder2-15B",
                "WizardAI/WizardCoder-33B",
            ],
            requires_endpoint=True,
            rate_limit=30,
        ),
        Provider.CLOUDFLARE: ProviderConfig(
            name=Provider.CLOUDFLARE,
            base_url="https://api.cloudflare.com/client/v4/workers",
            api_key_env="CLOUDFLARE_AI_API_TOKEN",
            models=[
                "@cf/meta/llama-3.1-70b-instruct",
                "@cf/mistral/mistral-7b-instruct-v0.2",
                "@cf/deepseek-ai/deepseek-coder-6.7b",
            ],
            requires_endpoint=True,
            rate_limit=1000,
        ),
        Provider.TOGETHER: ProviderConfig(
            name=Provider.TOGETHER,
            base_url="https://api.together.xyz/v1",
            api_key_env="TOGETHER_API_KEY",
            models=[
                "meta-llama/Llama-3.3-70B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "Qwen/Qwen2.5-72B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct",
                "deepseek-ai/DeepSeek-Coder-V2-Instruct",
            ],
            rate_limit=30,
        ),
        # Mistral AI - REQUIRES PAID KEY
        Provider.MISTRAL: ProviderConfig(
            name=Provider.MISTRAL,
            base_url="https://api.mistral.ai/v1",
            api_key_env="MISTRAL_API_KEY",
            models=[
                "mistral-small-latest",
                "mistral-medium-latest",
                "mistral-large-latest",
            ],
            rate_limit=30,
        ),
        # Cohere - REQUIRES PAID KEY
        Provider.COHERE: ProviderConfig(
            name=Provider.COHERE,
            base_url="https://api.cohere.ai/v1",
            api_key_env="COHERE_API_KEY",
            models=[
                "command-r-plus",
                "command-r",
                "command",
            ],
            rate_limit=30,
        ),
        # Perplexity - REQUIRES PAID KEY
        Provider.PERPLEXITY: ProviderConfig(
            name=Provider.PERPLEXITY,
            base_url="https://api.perplexity.ai",
            api_key_env="PERPLEXITY_API_KEY",
            models=[
                "sonar",
                "sonar-pro",
            ],
            rate_limit=30,
        ),
        # DeepSeek - REQUIRES PAID KEY
        Provider.DEEPSEEK: ProviderConfig(
            name=Provider.DEEPSEEK,
            base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            models=[
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-reasoner",
            ],
            rate_limit=30,
        ),
    }

    def __init__(self):
        self.stats = RouterStats()
        self.cooldowns: Dict[str, float] = {}
        self._local = threading.local()
        self.circuit_config = CircuitBreakerConfig()
        # Skill middleware
        self.middleware = get_middleware() if MIDDLEWARE_AVAILABLE else None

    def _is_circuit_open(self, provider: Provider) -> bool:
        """Check if circuit breaker is open for provider."""
        key = provider.value
        if key in self.stats.circuit_open_until:
            if time.time() < self.stats.circuit_open_until[key]:
                return True
            # Recovery timeout passed, try half-open
            del self.stats.circuit_open_until[key]
        return False

    def _record_success(self, provider: Provider, model: str):
        """Record success and reset circuit breaker."""
        key = provider.value
        self.stats.failures_since_success[key] = 0
        if key in self.stats.circuit_open_until:
            del self.stats.circuit_open_until[key]

    def _record_failure(self, provider: Provider, model: str = None, error: str = None):
        """Record failure and potentially open circuit."""
        key = provider.value
        self.stats.failures_since_success[key] = self.stats.failures_since_success.get(key, 0) + 1
        self.stats.failures[key] = self.stats.failures.get(key, 0) + 1

        if self.stats.failures_since_success[key] >= self.circuit_config.failure_threshold:
            self.stats.circuit_open_until[key] = time.time() + self.circuit_config.recovery_timeout
            self.stats.failures_since_success[key] = 0  # Reset counter after circuit opens

    def _get_api_key(self, provider: Provider) -> Optional[str]:
        """Get API key from environment using new key management system."""
        # Use new key management for consistency
        keys = get_provider_keys(provider.value)
        if not keys:
            return None

        # Round-robin selection (use thread-local index)
        if not hasattr(self._local, 'key_indices'):
            self._local.key_indices = {}

        if provider.value not in self._local.key_indices:
            self._local.key_indices[provider.value] = 0

        idx = self._local.key_indices[provider.value] % len(keys)
        self._local.key_indices[provider.value] = idx + 1

        return keys[idx]

    def _is_cooldown(self, provider: Provider) -> bool:
        """Check if provider is unavailable (cooldown or circuit open)."""
        # Check circuit breaker first
        if self._is_circuit_open(provider):
            return True

        key = provider.value
        if key not in self.cooldowns:
            return False

        elapsed = time.time() - self.cooldowns[key]
        config = self.PROVIDERS[provider]

        if elapsed < config.cooldown:
            return True

        # Clear expired cooldown
        del self.cooldowns[key]
        return False

    def _set_cooldown(self, provider: Provider):
        """Set provider to cooldown."""
        self.cooldowns[provider.value] = time.time()

    def _call_groq(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Groq API."""
        try:
            from groq import Groq
        except ImportError:
            return {"error": "pip install groq"}

        api_key = self._get_api_key(Provider.GROQ)
        if not api_key:
            return {"error": "No Groq API key found"}

        try:
            client = Groq(api_key=api_key)

            # Filter kwargs for Groq API
            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "top_p", "stop"]
            }

            # Use full model ID as-is (Groq supports "openai/gpt-oss-120b", "qwen/qwen3-32b")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **clean_kwargs
            )

            self._record_success(Provider.GROQ, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "groq",
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                }
            }
        except Exception as e:
            error_msg = str(e)
            self._record_failure(Provider.GROQ, model, error_msg)
            # Make error message more readable
            if "authentication" in error_msg.lower() or "401" in error_msg:
                error_msg = "Invalid API key or authentication failed"
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                error_msg = "Rate limit exceeded - will retry"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                error_msg = "Connection error - check network"
            return {"error": error_msg}

    def _call_openrouter(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call OpenRouter API."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}

        api_key = self._get_api_key(Provider.OPENROUTER)
        if not api_key:
            return {"error": "No OpenRouter API key found"}

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )

            # Filter kwargs
            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "top_p", "stop"]
            }

            # OpenRouter uses full model names - only prefix if it's a known OpenRouter model
            # Don't use google/ prefix for Gemini (use official Google provider instead)
            openrouter_model = model  # Use model as-is (should have / prefix for OpenRouter models)
            response = client.chat.completions.create(
                model=openrouter_model,
                messages=messages,
                **clean_kwargs
            )

            self._record_success(Provider.OPENROUTER, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "openrouter",
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                }
            }
        except Exception as e:
            error_msg = str(e)
            self._record_failure(Provider.OPENROUTER, model, error_msg)
            # Provide helpful error messages
            if "API key" in error_msg.lower() or "401" in error_msg or "auth" in error_msg.lower():
                error_msg = "Invalid OpenRouter API key"
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                error_msg = "OpenRouter rate limit exceeded"
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = "Model not available on OpenRouter"
            return {"error": error_msg}

    def _call_huggingface(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call HuggingFace Inference API."""
        api_key = self._get_api_key(Provider.HUGGINGFACE)
        if not api_key:
            return {"error": "No HuggingFace token found"}

        try:
            import requests

            # Convert messages to single text
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

            response = requests.post(
                f"{self.PROVIDERS[Provider.HUGGINGFACE].base_url}/{model}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": text},
                timeout=120
            )

            if response.status_code == 200:
                self._record_success(Provider.HUGGINGFACE, model)
                return {
                    "content": response.json()[0].get("generated_text", ""),
                    "provider": "huggingface",
                    "model": model,
                }
            else:
                self._record_failure(Provider.HUGGINGFACE, model, response.text)
                return {"error": f"HF API error: {response.status_code}"}

        except Exception as e:
            self._record_failure(Provider.HUGGINGFACE, model, str(e))
            return {"error": str(e)}

    def _call_cloudflare(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Cloudflare Workers AI."""
        api_key = self._get_api_key(Provider.CLOUDFLARE)
        if not api_key:
            return {"error": "No Cloudflare API token found"}

        try:
            import requests

            # Convert messages
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages if m.get("content")])

            response = requests.post(
                f"https://api.cloudflare.com/client/v4/workers/{model}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"prompt": text},
                timeout=120
            )

            if response.status_code == 200:
                self._record_success(Provider.CLOUDFLARE, model)
                return {
                    "content": response.json().get("result", {}).get("response", ""),
                    "provider": "cloudflare",
                    "model": model,
                }
            else:
                self._record_failure(Provider.CLOUDFLARE, model, response.text)
                return {"error": f"CF error: {response.status_code}"}

        except Exception as e:
            self._record_failure(Provider.CLOUDFLARE, model, str(e))
            return {"error": str(e)}

    def _call_together(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Together AI."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}

        api_key = self._get_api_key(Provider.TOGETHER)
        if not api_key:
            return {"error": "No Together AI key found"}

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )

            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens"]
            }

            response = client.chat.completions.create(
                model=model.split("/")[-1] if model else "meta-llama/Llama-3.3-70B-Instruct",
                messages=messages,
                **clean_kwargs
            )

            self._record_success(Provider.TOGETHER, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "together",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.TOGETHER, model, str(e))
            return {"error": str(e)}

    def _call_mistral(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Mistral AI."""
        try:
            from mistralai.client import MistralClient
        except ImportError:
            return {"error": "pip install mistralai"}

        api_key = self._get_api_key(Provider.MISTRAL)
        if not api_key:
            return {"error": "No Mistral API key found"}

        try:
            client = MistralClient(api_key=api_key)

            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "top_p"]
            }

            response = client.chat(
                model=model,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                **clean_kwargs
            )

            self._record_success(Provider.MISTRAL, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "mistral",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.MISTRAL, model, str(e))
            return {"error": str(e)}

    def _call_cohere(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Cohere API."""
        try:
            import cohere
        except ImportError:
            return {"error": "pip install cohere"}

        api_key = self._get_api_key(Provider.COHERE)
        if not api_key:
            return {"error": "No Cohere API key found"}

        try:
            client = cohere.Client(api_key=api_key)

            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "p", "frequency_penalty", "presence_penalty"]
            }

            response = client.chat(
                model=model,
                message=messages[-1]["content"] if messages else "",
                chat_history=[{"role": m["role"], "message": m["content"]} for m in messages[:-1]],
                **clean_kwargs
            )

            self._record_success(Provider.COHERE, model)

            return {
                "content": response.text,
                "provider": "cohere",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.COHERE, model, str(e))
            return {"error": str(e)}

    def _call_deepseek_api(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call DeepSeek Direct API."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}

        api_key = self._get_api_key(Provider.DEEPSEEK)
        if not api_key:
            return {"error": "No DeepSeek API key found"}

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )

            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens"]
            }

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **clean_kwargs
            )

            self._record_success(Provider.DEEPSEEK, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "deepseek",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.DEEPSEEK, model, str(e))
            return {"error": str(e)}

    def _call_perplexity(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Perplexity AI API."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}

        api_key = self._get_api_key(Provider.PERPLEXITY)
        if not api_key:
            return {"error": "No Perplexity API key found"}

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )

            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens"]
            }

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **clean_kwargs
            )

            self._record_success(Provider.PERPLEXITY, model)

            return {
                "content": response.choices[0].message.content,
                "provider": "perplexity",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.PERPLEXITY, model, str(e))
            return {"error": str(e)}

    def _record_success(self, provider: Provider, model: str):
        """Record successful call and reset provider circuit state."""
        with self.stats.lock:
            self.stats.total_calls += 1
            self.stats.provider_calls[provider.value] = self.stats.provider_calls.get(provider.value, 0) + 1
            self.stats.last_used[provider.value] = time.time()
            self.stats.failures_since_success[provider.value] = 0
            self.stats.circuit_open_until.pop(provider.value, None)

    def _record_failure(self, provider: Provider, model: str, error: str):
        """Record failed call and apply cooldown/circuit protection."""
        with self.stats.lock:
            self.stats.failures[provider.value] = self.stats.failures.get(provider.value, 0) + 1
            self.stats.failures_since_success[provider.value] = (
                self.stats.failures_since_success.get(provider.value, 0) + 1
            )

            if self.stats.failures_since_success[provider.value] >= self.circuit_config.failure_threshold:
                self.stats.circuit_open_until[provider.value] = time.time() + self.circuit_config.recovery_timeout
                self.stats.failures_since_success[provider.value] = 0

            # Apply cooldown on repeated failures for backward-compatible health behavior
            if self.stats.failures[provider.value] >= 3:
                self._set_cooldown(provider)
                self.stats.failures[provider.value] = 0

    def _call_gemini(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Gemini API using official google-genai SDK (new unified SDK for Gemini 2.0+)."""
        try:
            from google import genai
        except ImportError:
            return {"error": "google-genai not installed: pip install google-genai"}

        api_key = self._get_api_key(Provider.GOOGLE)
        if not api_key:
            return {"error": "No Google Gemini API key found"}

        try:
            client = genai.Client(api_key=api_key)

            # Convert messages format for Gemini
            # Combine system prompt with first user message if present
            combined_content = ""
            for msg in messages:
                if msg["role"] == "system":
                    combined_content += f"[System] {msg['content']}\n\n"
                elif msg["role"] == "user":
                    combined_content += f"[User] {msg['content']}"
            
            # Ensure model name is in correct format (e.g., "gemini-2.0-flash")
            if not model.startswith("gemini"):
                model = f"gemini-{model}"

            # Filter kwargs for Gemini API
            config = {}
            if "temperature" in kwargs:
                config["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                config["max_output_tokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                config["top_p"] = kwargs["top_p"]

            response = client.models.generate_content(
                model=model,
                contents=combined_content,
                config=genai.types.GenerateContentConfig(**config) if config else None
            )

            self._record_success(Provider.GOOGLE, model)

            return {
                "content": response.text,
                "provider": "google",
                "model": model,
            }
        except Exception as e:
            error_msg = str(e)
            self._record_failure(Provider.GOOGLE, model, error_msg)
            if "API_KEY" in error_msg or "auth" in error_msg.lower():
                error_msg = "Invalid Gemini API key"
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_msg = "Gemini quota exceeded"
            return {"error": error_msg}

    def _get_available_providers(self) -> List[Provider]:
        """Get list of available providers (have keys, not in cooldown)."""
        available = []
        for provider in Provider:
            if has_provider(provider.value):
                if not self._is_cooldown(provider):
                    available.append(provider)
        return available

    def complete(self, messages: List[Dict], model: Optional[str] = None,
                 preferred_provider: Optional[Provider] = None,
                 task_type: Optional[str] = None,  # NEW: task-based routing
                 skills: Optional[List[str]] = None,
                 max_tokens: int = 4096,
                 **kwargs) -> Dict[str, Any]:
        """
        Complete a request with smart provider selection AND skill integration.

        Args:
            messages: Chat messages
            model: Preferred model (optional, will auto-select if not provided)
            preferred_provider: Provider preference (optional)
            task_type: Task category for model selection (optional, uses TASK_CATEGORIES)
            skills: Active skills for middleware (optional)
            **kwargs: Additional API parameters

        Returns:
            Dict with content, provider, model, usage info
        """
        from neuro.models import TASK_CATEGORIES

        # Get models based on task_type
        models_to_try = []
        if task_type and task_type in TASK_CATEGORIES:
            config = TASK_CATEGORIES[task_type]
            models_to_try = [config["primary"]] + config.get("fallback", [])
        elif model:
            models_to_try = [model]
        else:
            models_to_try = UNKNOWN_TASK_MODEL_CHAIN.copy()

        # NEW: Apply skill middleware pre-processing
        if MIDDLEWARE_AVAILABLE and self.middleware:
            if skills:
                self.middleware.set_skills(skills)
            messages = self.middleware.preprocess(messages)

        # Get available providers
        available = self._get_available_providers()
        if not available:
            return {"error": "No API providers available. Set GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY"}

        # Build priority list
        if preferred_provider and preferred_provider in available:
            providers_to_try = [preferred_provider] + [p for p in available if p != preferred_provider]
        else:
            providers_to_try = available

        # Map model configs to providers (extract provider from model string)
        def get_provider_from_model(model_config: str) -> Provider:
            if model_config.startswith("gemini-"):
                return Provider.GOOGLE
            if "/" in model_config:
                parts = model_config.split("/")
                provider_name = parts[0].lower()
            else:
                return Provider.OPENROUTER

            provider_map = {
                "google": Provider.GOOGLE, "gemini": Provider.GOOGLE,
                "groq": Provider.GROQ, "openrouter": Provider.OPENROUTER,
                "huggingface": Provider.HUGGINGFACE, "cloudflare": Provider.CLOUDFLARE,
                "together": Provider.TOGETHER, "deepseek": Provider.OPENROUTER,
                "qwen": Provider.OPENROUTER, "cohere": Provider.OPENROUTER,
                "nvidia": Provider.OPENROUTER,
            }
            return provider_map.get(provider_name, Provider.OPENROUTER)

        # Try each model in task-based order
        for model_config in models_to_try:
            provider = get_provider_from_model(model_config)

            if provider not in providers_to_try:
                continue
            if self._is_cooldown(provider):
                continue

            # Extract model name from config
            if "/" in model_config:
                model = "/".join(model_config.split("/")[1:])
            else:
                model = model_config

            call_kwargs = {**kwargs, "max_tokens": max_tokens}
            if provider == Provider.GOOGLE:
                result = self._call_gemini(model, messages, **call_kwargs)
            elif provider == Provider.GROQ:
                result = self._call_groq(model, messages, **call_kwargs)
            elif provider == Provider.OPENROUTER:
                result = self._call_openrouter(model, messages, **call_kwargs)
            elif provider == Provider.HUGGINGFACE:
                result = self._call_huggingface(model, messages, **call_kwargs)
            elif provider == Provider.CLOUDFLARE:
                result = self._call_cloudflare(model, messages, **call_kwargs)
            elif provider == Provider.TOGETHER:
                result = self._call_together(model, messages, **call_kwargs)
            else:
                continue

            # Add error details to the response
        errors = []
        for model_config in models_to_try:
            provider = get_provider_from_model(model_config)
            if provider not in providers_to_try:
                continue
            if self._is_cooldown(provider):
                errors.append(f"{provider.value}: cooldown")
                continue
            
            if "/" in model_config:
                model = "/".join(model_config.split("/")[1:])
            else:
                model = model_config
            
            call_kwargs = {**kwargs, "max_tokens": max_tokens}
            if provider == Provider.GOOGLE:
                result = self._call_gemini(model, messages, **call_kwargs)
            elif provider == Provider.GROQ:
                result = self._call_groq(model, messages, **call_kwargs)
            elif provider == Provider.OPENROUTER:
                result = self._call_openrouter(model, messages, **call_kwargs)
            elif provider == Provider.HUGGINGFACE:
                result = self._call_huggingface(model, messages, **call_kwargs)
            elif provider == Provider.CLOUDFLARE:
                result = self._call_cloudflare(model, messages, **call_kwargs)
            elif provider == Provider.TOGETHER:
                result = self._call_together(model, messages, **call_kwargs)
            else:
                continue
            
            if "error" in result:
                errors.append(f"{provider.value}: {result['error'][:50]}")
            else:
                if MIDDLEWARE_AVAILABLE and self.middleware:
                    result = self.middleware.postprocess(result)
                return result
        
        return {"error": "All providers failed", "details": errors}

    def chat(self, prompt: str, task_type: str = "code_generation",
             max_tokens: int = 4096, system: str = None) -> str:
        """
        Simple chat interface. Routes to best model for task type.
        Returns the response text string. Falls back through providers on failure.
        """
        from neuro.models import TASK_CATEGORIES

        # Get model for task type
        if task_type in TASK_CATEGORIES:
            primary = TASK_CATEGORIES[task_type]["primary"]
            fallbacks = TASK_CATEGORIES[task_type].get("fallback", [])
        else:
            primary = UNKNOWN_TASK_MODEL_CHAIN[0]
            fallbacks = UNKNOWN_TASK_MODEL_CHAIN[1:]

        models_to_try = [primary] + [m for m in fallbacks if m != primary]

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Try all models in the fallback chain (removed depth cap for deeper fallback)
        for model_config in models_to_try:
            try:
                # Extract provider and model from config
                if "/" in model_config:
                    parts = model_config.split("/")
                    provider = parts[0].lower()
                    model = "/".join(parts[1:])
                elif model_config.startswith("gemini-"):
                    provider = "google"
                    model = model_config
                else:
                    provider = "openrouter"
                    model = model_config

                # Map provider to enum
                provider_map = {
                    "google": Provider.GOOGLE,
                    "gemini": Provider.GOOGLE,
                    "google": Provider.GOOGLE,
                    "groq": Provider.GROQ,
                    "openrouter": Provider.OPENROUTER,
                    "huggingface": Provider.HUGGINGFACE,
                    "cloudflare": Provider.CLOUDFLARE,
                    "together": Provider.TOGETHER,
                    "deepseek": Provider.DEEPSEEK,
                    "qwen": Provider.OPENROUTER,  # Via OpenRouter
                    "mistral": Provider.MISTRAL,
                    "cohere": Provider.COHERE,
                    "perplexity": Provider.PERPLEXITY,
                }

                provider_enum = provider_map.get(provider, Provider.OPENROUTER)

                # Call the provider
                if provider_enum == Provider.GOOGLE:
                    result = self._call_gemini(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.GROQ:
                    result = self._call_groq(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.OPENROUTER:
                    result = self._call_openrouter(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.HUGGINGFACE:
                    result = self._call_huggingface(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.CLOUDFLARE:
                    result = self._call_cloudflare(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.TOGETHER:
                    result = self._call_together(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.MISTRAL:
                    result = self._call_mistral(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.COHERE:
                    result = self._call_cohere(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.DEEPSEEK:
                    result = self._call_deepseek_api(model, messages, max_tokens=max_tokens)
                elif provider_enum == Provider.PERPLEXITY:
                    result = self._call_perplexity(model, messages, max_tokens=max_tokens)
                else:
                    continue

                if "error" not in result and "content" in result:
                    return result["content"]

            except Exception:
                continue

        return ""  # All providers failed

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        with self.stats.lock:
            return {
                "total_calls": self.stats.total_calls,
                "provider_calls": dict(self.stats.provider_calls),
                "failures": dict(self.stats.failures),
                "last_used": dict(self.stats.last_used),
            }

    def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health = {}
        for provider in self.PROVIDERS.keys():  # Only iterate over configured providers
            config = self.PROVIDERS[provider]
            has_key = bool(self._get_api_key(provider))
            in_cooldown = self._is_cooldown(provider)
            health[provider.value] = {
                "available": has_key and not in_cooldown,
                "has_key": has_key,
                "in_cooldown": in_cooldown,
                "models": len(config.models),
            }
        return health


# Global router instance
_router = SmartRouter()


def complete(messages: List[Dict], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for router.complete()

    Usage:
        from neuro.router import complete

        result = complete(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gemini-3.5-flash"
        )

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Response: {result['content']}")
    """
    return _router.complete(messages, model, **kwargs)


def health_check() -> Dict[str, Any]:
    """Check which providers are healthy."""
    return _router.health_check()


def get_stats() -> Dict[str, Any]:
    """Get router statistics."""
    return _router.get_stats()
