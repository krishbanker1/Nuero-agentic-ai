# Neuro Model Registry - Cleaned & Deduplicated
# Task-to-Model Assignment with 20 Categories - Free-first production app routing
# Last saved: 2026-05-30

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ModelRole(Enum):
    """Model roles for task routing."""
    PLANNER = "planner"      # Task decomposition, planning
    ARCHITECT = "architect"  # System design, architecture
    CODER = "coder"         # Code implementation
    DEBUGGER = "debugger"   # Error analysis and fixing
    VALIDATOR = "validator" # Test validation, checking
    REFACTOR = "refactor"    # Code cleanup, refactoring
    REVIEWER = "reviewer"    # Code review, security audit
    FRONTEND = "frontend"    # UI/UX, frontend tasks
    DOCUMENTATION = "doc"    # Documentation generation


@dataclass
class ModelMetadata:
    """Structured metadata for a model."""
    name: str
    provider: str
    roles: List[str]
    strengths: List[str]
    priority: int  # 1 = highest
    fallback_priority: int
    cost: str  # "free", "cheap", "expensive"
    requires_key: bool
    context_window: Optional[int]
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "roles": self.roles,
            "strengths": self.strengths,
            "priority": self.priority,
            "fallback_priority": self.fallback_priority,
            "cost": self.cost,
            "requires_key": self.requires_key,
            "context_window": self.context_window,
            "enabled": self.enabled,
        }


APPROVED_PROVIDERS = frozenset({
    'google', 'groq', 'openrouter', 'together', 'huggingface',
    'cloudflare', 'cohere', 'lepton', 'mistral', 'perplexity'
})

# All 50+ models with structured metadata
MODEL_REGISTRY: List[ModelMetadata] = [
    # =============================================================================
    # GOOGLE GEMINI MODELS (native Google GenAI SDK IDs, no OpenRouter prefixes)
    # =============================================================================
    ModelMetadata(
        name="gemini-3.5-flash",
        provider="google",
        roles=["planner", "architect", "frontend", "reviewer"],
        strengths=["advanced_reasoning", "long_context", "multimodal", "planning"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-3-flash-preview",
        provider="google",
        roles=["planner", "architect"],
        strengths=["latest_features", "reasoning", "long_context"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-2.5-flash",
        provider="google",
        roles=["validator", "debugger", "documentation", "researcher"],
        strengths=["fast", "reliable", "reasoning", "multimodal"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-2.5-flash-lite",
        provider="google",
        roles=["router", "summarizer", "json", "documentation"],
        strengths=["fast", "cheap", "classification", "summarization"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-3.1-flash-live-preview",
        provider="google",
        roles=["voice", "realtime"],
        strengths=["realtime", "audio", "voice"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-2.5-flash-native-audio-preview-12-2025",
        provider="google",
        roles=["voice", "audio"],
        strengths=["native_audio", "realtime"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-3.1-flash-tts-preview",
        provider="google",
        roles=["tts", "narration"],
        strengths=["tts", "voice_output"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-2.5-flash-preview-tts",
        provider="google",
        roles=["tts", "narration"],
        strengths=["tts", "fallback_voice"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-2.5-flash-image",
        provider="google",
        roles=["image", "vision", "frontend"],
        strengths=["image_generation", "image_editing", "vision"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini-embedding-2",
        provider="google",
        roles=["embedding", "memory", "rag"],
        strengths=["embedding", "semantic_search", "rag"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=8192,
    ),
    ModelMetadata(
        name="gemini-embedding-001",
        provider="google",
        roles=["embedding", "memory", "rag"],
        strengths=["embedding", "semantic_search", "fallback"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=8192,
    ),

    # =============================================================================
    # GROQ MODELS (6 models)
    # =============================================================================


    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="groq",
        roles=["planner", "architect", "coder", "debugger", "refactor"],
        strengths=["fast", "reasoning", "code", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/llama-3.1-8b-instant",
        provider="groq",
        roles=["coder", "frontend", "documentation"],
        strengths=["fast", "cheap"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/qwen/qwen3-32b",
        provider="groq",
        roles=["coder", "debugger", "planner"],
        strengths=["code", "reasoning", "fast"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="groq/llama-4-scout-17b-16e-instruct",
        provider="groq",
        roles=["coder", "frontend"],
        strengths=["code", "fast"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=100000,
    ),
    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="groq",
        roles=["frontend", "architect", "reviewer"],
        strengths=["vision", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/mixtral-8x7b-32768",
        provider="groq",
        roles=["planner", "architect"],
        strengths=["reasoning", "long-context"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32768,
    ),
    # NEW: Llama 4 Maverick - Latest Groq model for competitive coding
    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="groq",
        roles=["coder", "debugger", "planner"],
        strengths=["code", "reasoning", "fast", "latest"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),


    # =============================================================================
    # NEW: Llama 4 Maverick - Latest Groq model for competitive coding
    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="groq",
        roles=["coder", "debugger", "planner"],
        strengths=["code", "reasoning", "fast", "latest"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),

    # OPENROUTER FREE MODELS (20+ models)
    # =============================================================================
    ModelMetadata(
        name="openrouter/deepseek/deepseek-v4-flash:free",
        provider="openrouter",
        roles=["planner", "architect", "debugger", "validator"],
        strengths=["reasoning", "long-context", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen3-coder:free",
        provider="openrouter",
        roles=["coder", "debugger", "validator"],
        strengths=["code", "fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen3-next-80b-a3b-instruct:free",
        provider="openrouter",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/google/gemma-4-31b-it:free",
        provider="openrouter",
        roles=["frontend", "architect", "refactor"],
        strengths=["reasoning", "frontend", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/google/gemma-4-26b-a4b-it:free",
        provider="openrouter",
        roles=["frontend", "coder"],
        strengths=["frontend", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/meta-llama/llama-3.3-70b-instruct:free",
        provider="openrouter",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="openrouter/meta-llama/llama-3.2-3b-instruct:free",
        provider="openrouter",
        roles=["documentation", "frontend"],
        strengths=["fast", "cheap", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        provider="openrouter",
        roles=["architect", "reviewer", "security"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/poolside/laguna-m.1:free",
        provider="openrouter",
        roles=["coder"],
        strengths=["code", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/baidu/cobuddy:free",
        provider="openrouter",
        roles=["frontend", "documentation"],
        strengths=["frontend", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/z-ai/glm-4.5-air:free",
        provider="openrouter",
        roles=["coder", "planner"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/inflection/inflection-3-pi:free",
        provider="openrouter",
        roles=["planner", "architect"],
        strengths=["reasoning", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/mistralai/mistral-nemo:free",
        provider="openrouter",
        roles=["coder", "frontend"],
        strengths=["code", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/anthropic/claude-3-haiku:free",
        provider="openrouter",
        roles=["debugger", "validator"],
        strengths=["fast", "reasoning", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=200000,
    ),
    ModelMetadata(
        name="openrouter/microsoft/phi-4:free",
        provider="openrouter",
        roles=["coder", "debugger"],
        strengths=["code", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=16000,
    ),
    ModelMetadata(
        name="openrouter/google/gemma-4-31b-it:free",
        provider="openrouter",
        roles=["documentation", "frontend"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    # Qwen via OpenRouter (user specified Qwen/DeepSeek use OpenRouter)
    ModelMetadata(
        name="openrouter/qwen/qwen3-32b",
        provider="openrouter",
        roles=["coder", "planner", "debugger"],
        strengths=["code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen2.5-72b-instruct",
        provider="openrouter",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    # DeepSeek via OpenRouter
    ModelMetadata(
        name="openrouter/deepseek/deepseek-coder-v2",
        provider="openrouter",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="openrouter/deepseek/deepseek-chat",
        provider="openrouter",
        roles=["planner", "debugger"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),

    # =============================================================================
    # NEW: OpenAI OSS 120B - Complex reasoning powerhouse
    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="openrouter",
        roles=["architect", "planner", "reviewer"],
        strengths=["reasoning", "complex-tasks", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=200000,
    ),
    # NEW: DeepSeek V3 - Top free reasoning model (strong code-repair performance)
    ModelMetadata(
        name="openrouter/deepseek/deepseek-v4-flash:free",
        provider="openrouter",
        roles=["planner", "architect", "coder", "reasoning"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),

    # TOGETHER AI MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="together/llama-3.3-70b-instruct",
        provider="together",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="together/qwen-2.5-72b-instruct",
        provider="together",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/qwen-2.5-coder-32b-instruct",
        provider="together",
        roles=["coder", "debugger"],
        strengths=["code", "fast"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/mixtral-8x7b-instruct",
        provider="together",
        roles=["coder", "planner"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/deepseek-coder-v2-instruct",
        provider="together",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=64000,
    ),

    # =============================================================================
    # HUGGINGFACE MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="huggingface/Qwen2.5-Coder-32B-Instruct",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="huggingface/DeepSeek-Coder-V2",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="huggingface/CodeLlama-70B-Instruct",
        provider="huggingface",
        roles=["coder", "reviewer"],
        strengths=["code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=16000,
    ),
    ModelMetadata(
        name="huggingface/Starcoder2-15B",
        provider="huggingface",
        roles=["coder"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=14000,
    ),
    ModelMetadata(
        name="huggingface/WizardCoder-33B",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=18000,
    ),

    # =============================================================================
    # CLOUDFLARE MODELS (3 models)
    # =============================================================================
    ModelMetadata(
        name="cloudflare/@cf/meta/llama-3.1-70b-instruct",
        provider="cloudflare",
        roles=["planner", "architect", "coder"],
        strengths=["fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cloudflare/@cf/mistral/mistral-7b-instruct-v0.2",
        provider="cloudflare",
        roles=["coder", "frontend"],
        strengths=["fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="cloudflare/@cf/deepseek-ai/deepseek-coder-6.7b",
        provider="cloudflare",
        roles=["coder", "debugger"],
        strengths=["code", "fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=16000,
    ),

    # =============================================================================
    # ADDITIONAL PROVIDERS
    # =============================================================================
    # Cohere (3 models)
    ModelMetadata(
        name="cohere/command-r-plus",
        provider="cohere",
        roles=["planner", "architect"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="expensive",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cohere/command-r",
        provider="cohere",
        roles=["planner", "coder"],
        strengths=["reasoning", "code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cohere/command",
        provider="cohere",
        roles=["coder", "frontend"],
        strengths=["fast"],
        priority=3,
        fallback_priority=4,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),

    # Lepton (2 models)
    ModelMetadata(
        name="lepton/llama-3.1-405b",
        provider="lepton",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="expensive",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="lepton/llama-3.1-8b",
        provider="lepton",
        roles=["coder", "documentation"],
        strengths=["fast", "cheap"],
        priority=3,
        fallback_priority=4,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),

    # Additional free models
    ModelMetadata(
        name="perplexity/llama-3.1-sonar-large",
        provider="perplexity",
        roles=["planner", "researcher"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="mistral/open-mixtral-8x22b",
        provider="mistral",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="expensive",
        requires_key=True,
        context_window=64000,
    ),
]


def _dedupe_model_registry(models: List[ModelMetadata]) -> List[ModelMetadata]:
    """Remove duplicate model names while preserving first-seen routing order."""
    seen = set()
    deduped: List[ModelMetadata] = []
    for model in models:
        if model.name in seen:
            continue
        seen.add(model.name)
        deduped.append(model)
    return deduped


MODEL_REGISTRY = _dedupe_model_registry(MODEL_REGISTRY)

# Legacy string-based list for backward compatibility
APPROVED_MODELS = [m.name for m in MODEL_REGISTRY]


def get_models_by_role(role: ModelRole) -> List[ModelMetadata]:
    """Get models filtered by role, sorted by priority."""
    filtered = [m for m in MODEL_REGISTRY if role.value in m.roles]
    return sorted(filtered, key=lambda x: x.priority)


def get_models_by_provider(provider: str) -> List[ModelMetadata]:
    """Get models filtered by provider."""
    return [m for m in MODEL_REGISTRY if m.provider == provider]


def get_free_models() -> List[ModelMetadata]:
    """Get all free models."""
    return [m for m in MODEL_REGISTRY if m.cost == "free"]


def get_model_by_name(name: str) -> Optional[ModelMetadata]:
    """Get model by full name."""
    for m in MODEL_REGISTRY:
        if m.name == name:
            return m
    return None


# =============================================================================
# TASK-to-MODEL ROUTING - Complete System Wiring
# =============================================================================
#
# PROVIDER MODEL CAPABILITIES:
# ---------------------------
# GEMINI (gemini-*):
#   - Best: coding, reasoning, multimodal (vision), 1M context, agentic
#   - Models: gemini-3.5-flash, gemini-2.5-flash, gemini-2.5-flash-lite
#
# GROQ (groq/*):
#   - GPT-OSS 120B: Best for complex reasoning, code review, architecture
#   - GPT-OSS 20B: Fast reasoning
#   - Qwen3-32B: Specialized coder, debugging, tests
#   - Llama-3.3-70B: Fast large model, general tasks
#   - Llama-3.1-8B: Ultra fast, quick tasks
#   - Compound/Compound-mini: Agentic with built-in tools
#
# OPENROUTER (openrouter/*:free):
#   - DeepSeek V4 Flash: Best free model overall
#   - Qwen3 Coder: Free specialized coding
#   - Llama 3.3 70B: Free large model
#   - Gemma 4: Fast reasoning
#
# HUGGINGFACE (huggingface/*):
#   - Qwen2.5-Coder-32B: Free coding
#   - DeepSeek-Coder-V2: Free coding
#
# CLOUDFLARE (@cf/*):
#   - Llama-70B: Free inference
#   - Mistral-7B: Free inference
#   - DeepSeek-Coder-6.7B: Free coding

TASK_CATEGORIES = {
    # ==========================================================================
    # CODE & DEVELOPMENT TASKS
    # ==========================================================================

    # 1. CODE GENERATION - Full app/feature implementation
    "code_generation": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "groq/qwen/qwen3-32b"],
        "roles": ["coder", "planner"],
        "description": "Full app/feature implementation"
    },

    # 2. DEEP REASONING - Complex analysis and planning
    "deep_reasoning": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "groq/qwen/qwen3-32b"],
        "roles": ["planner", "architect"],
        "description": "Complex reasoning, planning, analysis"
    },

    # 3. BUG DETECTION - Finding bugs and issues
    "bug_detection": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["debugger", "coder"],
        "description": "Bug finding and diagnosis"
    },

    # 4. DEBUGGING - Error fixing, stack trace analysis
    "debugging": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["debugger", "coder"],
        "description": "Error fixing, stack trace analysis"
    },

    # 5. CODE REVIEW - PR reviews, quality assessment
    "code_review": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "groq/qwen/qwen3-32b"],
        "roles": ["reviewer", "architect"],
        "description": "PR reviews, quality assessment"
    },

    # 6. TEST WRITING - Unit tests, integration tests
    "test_writing": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["validator", "coder"],
        "description": "Unit tests, integration tests"
    },

    # 7. TESTING QA - QA automation, E2E tests
    "testing_qa": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/qwen/qwen3-32b", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["validator", "coder"],
        "description": "QA automation, E2E tests"
    },

    # 8. REFACTORING - Code restructuring, optimization
    "refactoring": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "groq/qwen/qwen3-32b", "groq/llama-3.3-70b-versatile"],
        "roles": ["refactor", "reviewer"],
        "description": "Code restructuring, optimization"
    },
    "code_refactoring": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "groq/qwen/qwen3-32b", "groq/llama-3.3-70b-versatile"],
        "roles": ["refactor", "reviewer"],
        "description": "Code improvement, pattern application"
    },

    # 9. CODE COMPLETION - Autocomplete, snippets
    "code_completion": {
        "primary": "gemini-2.5-flash-lite",
        "fallback": ["groq/llama-3.1-8b-instant", "gemini-2.5-flash", "openrouter/qwen/qwen3-coder:free"],
        "roles": ["coder"],
        "description": "Autocomplete, snippet generation"
    },

    # ==========================================================================
    # FRONTEND & UI TASKS
    # ==========================================================================

    # 10. FRONTEND REACT - React, Next.js, Vue, Svelte
    "frontend_react": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder"],
        "description": "React, Next.js, Vue, Svelte"
    },

    # 11. FRONTEND UI - HTML/CSS, UI components
    "frontend_ui": {
        "primary": "gemini-3.5-flash",
        "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder"],
        "description": "HTML/CSS, UI components"
    },

    # 12. WEBSITE BUILDER - Full website generation
    "website_builder": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder", "designer"],
        "description": "Full website generation with HTML/CSS/JS"
    },

    # 13. APP BUILDER - Enterprise app generation
    "app_builder": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder", "architect"],
        "description": "Enterprise app generation (React, Vue, etc)"
    },

    # ==========================================================================
    # BACKEND & API TASKS
    # ==========================================================================

    # 14. BACKEND API - REST, GraphQL, FastAPI, Node.js
    "backend_api": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "architect"],
        "description": "REST, GraphQL, FastAPI, backend logic"
    },

    # 15. API DEVELOPMENT - Express, Node.js, API design
    "api_development": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "architect"],
        "description": "API design, Express, Node.js"
    },

    # ==========================================================================
    # DATA & DATABASE TASKS
    # ==========================================================================

    # 16. DATABASE SQL - SQL, PostgreSQL, MongoDB, migrations
    "database_sql": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "architect"],
        "description": "SQL, PostgreSQL, MongoDB, migrations"
    },

    # 17. DATA ANALYSIS - Pandas, NumPy, analytics, Jupyter
    "data_analysis": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "planner"],
        "description": "Pandas, NumPy, analytics, Jupyter"
    },

    # ==========================================================================
    # DEVOPS & DEPLOYMENT
    # ==========================================================================

    # 18. DEVOPS DEPLOYMENT - Docker, K8s, CI/CD, AWS, GCP
    "devops_deployment": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "architect"],
        "description": "Docker, K8s, CI/CD, AWS, GCP"
    },

    # 19. GIT OPERATIONS - Git commands, PRs, merges
    "git_operations": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": ["gemini-2.5-flash-lite", "gemini-2.5-flash", "openrouter/meta-llama/llama-3.2-3b-instruct:free"],
        "roles": ["coder"],
        "description": "Git commands, PRs, merges"
    },

    # ==========================================================================
    # SECURITY & QUALITY
    # ==========================================================================

    # 20. SECURITY AUDIT - Vulnerability scanning, fixes
    "security_audit": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["reviewer", "debugger"],
        "description": "Vulnerability scanning, fixes"
    },

    # ==========================================================================
    # DOCUMENTATION & NATURAL LANGUAGE
    # ==========================================================================

    # 21. DOCUMENTATION - README, API docs, comments
    "documentation": {
        "primary": "gemini-2.5-flash",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.1-8b-instant", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["documentation"],
        "description": "README, API docs, comments"
    },

    # 22. NATURAL LANGUAGE - Chatbots, summarization, NLP
    "natural_language": {
        "primary": "gemini-3.5-flash",
        "fallback": ["gemini-2.5-flash", "groq/llama-3.1-8b-instant", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["planner"],
        "description": "Chatbots, summarization, NLP"
    },

    # 23. OFFICE DOCUMENT - Word, Excel, PowerPoint generation
    "office_document_generation": {
        "primary": "gemini-2.5-flash",
        "fallback": ["gemini-3.5-flash", "gemini-2.5-flash-lite", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["planner"],
        "description": "Word, Excel, PowerPoint generation"
    },

    # ==========================================================================
    # SPECIALIZED TASKS
    # ==========================================================================

    # 24. LONG CONTEXT - Large codebase, 1M+ context
    "long_context": {
        "primary": "gemini-3.5-flash",
        "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["architect", "planner"],
        "description": "Large codebase, 1M+ context"
    },

    # 25. MULTI_MODAL - Vision + text, image understanding
    "multi_modal": {
        "primary": "gemini-3.5-flash",
        "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder"],
        "description": "Image understanding, file processing"
    },

    # 26. MOBILE DEVELOPMENT - iOS, Android, React Native, Flutter
    "mobile_development": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["frontend", "coder"],
        "description": "iOS, Android, React Native, Flutter"
    },

    # 27. ML AI TASKS - ML pipelines, AI training
    "ml_ai_tasks": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["coder", "planner"],
        "description": "ML pipelines, AI training"
    },

    # 28. PERFORMANCE OPT - Profiling, caching, optimization
    "performance_opt": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/qwen/qwen3-32b", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["debugger", "refactor"],
        "description": "Profiling, caching, optimization"
    },
    "performance_optimization": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/qwen/qwen3-32b", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["debugger", "refactor"],
        "description": "Performance tuning, benchmarks"
    },

    # 29. ARCHITECTURE DESIGN - System design, microservices
    "architecture_design": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["architect", "planner"],
        "description": "System design, microservices, patterns"
    },

    # 30. REASONING PLANNING - Strategic planning, task decomposition
    "reasoning_planning": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["planner", "architect"],
        "description": "Strategic planning, task decomposition"
    },

    # 31. FAST RESPONSE - Quick answers, simple tasks
    "fast_response": {
        "primary": "gemini-2.5-flash-lite",
        "fallback": ["groq/llama-3.1-8b-instant", "gemini-2.5-flash", "openrouter/meta-llama/llama-3.2-3b-instruct:free"],
        "roles": ["coder"],
        "description": "Quick answers, simple tasks"
    },

    # 32. AGENTIC TASKS - Tasks requiring tools (browsing, code execution)
    "agentic_tasks": {
        "primary": "groq/groq/compound",
        "fallback": ["gemini-3.5-flash", "groq/groq/compound-mini", "openrouter/deepseek/deepseek-v4-flash:free"],
        "roles": ["agent", "planner", "coder"],
        "description": "Tasks requiring tools (browsing, code execution)"
    },
}

# =============================================================================
# AGENT ROLE MODEL ASSIGNMENTS
# =============================================================================
# Maps agent roles to optimal models for each role

MODEL_ROLES = {
    # EXECUTOR - Primary code generator
    "executor": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "groq/qwen/qwen3-32b", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    # PLANNER - Strategic thinking, task breakdown
    "planner": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.3,
        "max_tokens": 8192,
    },
    # DEBUGGER - Bug finding, error analysis
    "debugger": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini-3.5-flash", "openrouter/qwen/qwen3-coder:free"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
    # REVIEWER - Code quality, PR reviews
    "reviewer": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.3-70b-versatile"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
    # VALIDATOR - Test writing, QA
    "validator": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini-3.5-flash", "openrouter/qwen/qwen3-coder:free"],
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    # ARCHITECT - System design, patterns
    "architect": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["gemini-3.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.3,
        "max_tokens": 8192,
    },
    # CODER - General coding tasks
    "coder": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "groq/qwen/qwen3-32b", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    # FRONTEND - UI/UX development
    "frontend": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "gemini-2.5-flash"],
        "temperature": 0.3,
        "max_tokens": 8192,
    },
    # DOCUMENTATION - Docs, README, comments
    "documentation": {
        "primary": "gemini-2.5-flash",
        "fallback": ["gemini-3.5-flash", "groq/llama-3.1-8b-instant"],
        "temperature": 0.4,
        "max_tokens": 4096,
    },
    # AGENT - Tasks requiring tools
    "agent": {
        "primary": "groq/groq/compound",
        "fallback": ["gemini-3.5-flash", "groq/groq/compound-mini"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    # REFACTOR - Code improvement
    "refactor": {
        "primary": "gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "groq/qwen/qwen3-32b"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
}


# Balanced free-first routing policy: Gemini is native Google-only and is not
# the default coding model. OpenRouter Qwen/DeepSeek own code/debug paths.
TASK_CATEGORIES.update({
    "code_generation": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-chat:free", "openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash", "groq/qwen/qwen3-32b", "groq/llama-3.3-70b-versatile"], "roles": ["coder"], "description": "Full app/feature implementation"},
    "debugging": {"primary": "openrouter/deepseek/deepseek-v4-flash:free", "fallback": ["openrouter/deepseek/deepseek-chat:free", "openrouter/qwen/qwen3-coder:free", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"], "roles": ["debugger"], "description": "Error fixing, stack trace analysis"},
    "bug_detection": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"], "roles": ["debugger", "coder"], "description": "Bug finding and diagnosis"},
    "testing_qa": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-chat:free"], "roles": ["validator"], "description": "QA automation, E2E tests"},
    "test_writing": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-chat:free"], "roles": ["validator", "coder"], "description": "Unit tests, integration tests"},
    "refactoring": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"], "roles": ["refactor"], "description": "Code restructuring, optimization"},
    "code_refactoring": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash", "groq/llama-3.3-70b-versatile"], "roles": ["refactor"], "description": "Code improvement, pattern application"},
    "deep_reasoning": {"primary": "gemini-3.5-flash", "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/openrouter/owl-alpha", "groq/llama-3.3-70b-versatile"], "roles": ["planner", "architect"], "description": "Complex reasoning, planning, analysis"},
    "architecture_design": {"primary": "gemini-3.5-flash", "fallback": ["openrouter/deepseek/deepseek-chat:free", "groq/llama-3.3-70b-versatile", "openrouter/qwen/qwen3-coder:free"], "roles": ["architect"], "description": "System design, microservices, patterns"},
    "frontend_react": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["gemini-3.5-flash", "openrouter/z-ai/glm-4.5-air:free", "groq/llama-3.3-70b-versatile"], "roles": ["frontend", "coder"], "description": "React, Next.js, Vue, Svelte"},
    "frontend_ui": {"primary": "gemini-3.5-flash", "fallback": ["openrouter/qwen/qwen3-coder:free", "openrouter/z-ai/glm-4.5-air:free", "groq/llama-3.3-70b-versatile"], "roles": ["frontend"], "description": "HTML/CSS, UI components"},
    "documentation": {"primary": "gemini-2.5-flash", "fallback": ["groq/llama-3.3-70b-versatile", "groq/llama-3.3-70b-versatile", "openrouter/meta-llama/llama-3.3-70b-instruct:free"], "roles": ["documentation"], "description": "README, API docs, comments"},
    "fast_response": {"primary": "groq/llama-3.1-8b-instant", "fallback": ["gemini-2.5-flash-lite", "groq/llama-3.3-70b-versatile", "openrouter/openrouter/free"], "roles": ["router"], "description": "Quick answers, simple tasks"},
    "long_context": {"primary": "gemini-3.5-flash", "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/openrouter/owl-alpha", "groq/llama-3.3-70b-versatile"], "roles": ["planner", "architect"], "description": "Large codebase, 1M+ context"},
    "multi_modal": {"primary": "gemini-3.5-flash", "fallback": ["gemini-2.5-flash-image", "openrouter/qwen/qwen3-coder:free", "groq/llama-3.3-70b-versatile"], "roles": ["frontend", "vision"], "description": "Image understanding, file processing"},
})

MODEL_ROLES.update({
    "executor": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-chat:free", "openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash"], "temperature": 0.2, "max_tokens": 8192},
    "coder": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-chat:free", "openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash"], "temperature": 0.2, "max_tokens": 8192},
    "debugger": {"primary": "openrouter/deepseek/deepseek-v4-flash:free", "fallback": ["openrouter/deepseek/deepseek-chat:free", "openrouter/qwen/qwen3-coder:free", "gemini-2.5-flash"], "temperature": 0.1, "max_tokens": 4096},
    "validator": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["gemini-2.5-flash", "groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-chat:free"], "temperature": 0.2, "max_tokens": 4096},
    "planner": {"primary": "gemini-3.5-flash", "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/openrouter/owl-alpha", "groq/llama-3.3-70b-versatile"], "temperature": 0.3, "max_tokens": 8192},
    "architect": {"primary": "gemini-3.5-flash", "fallback": ["openrouter/deepseek/deepseek-chat:free", "groq/llama-3.3-70b-versatile", "openrouter/qwen/qwen3-coder:free"], "temperature": 0.3, "max_tokens": 8192},
    "frontend": {"primary": "gemini-3.5-flash", "fallback": ["openrouter/qwen/qwen3-coder:free", "openrouter/z-ai/glm-4.5-air:free", "groq/llama-3.3-70b-versatile"], "temperature": 0.3, "max_tokens": 8192},
    "documentation": {"primary": "gemini-2.5-flash", "fallback": ["groq/llama-3.3-70b-versatile", "groq/llama-3.3-70b-versatile"], "temperature": 0.4, "max_tokens": 4096},
    "reviewer": {"primary": "groq/llama-3.3-70b-versatile", "fallback": ["openrouter/deepseek/deepseek-chat:free", "gemini-3.5-flash"], "temperature": 0.1, "max_tokens": 4096},
    "refactor": {"primary": "openrouter/qwen/qwen3-coder:free", "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "gemini-2.5-flash"], "temperature": 0.2, "max_tokens": 8192},
})


# =============================================================================
# TASK TYPE DETECTION KEYWORDS
# =============================================================================
# Maps keywords to task types for automatic task detection

TASK_KEYWORDS = {
    "code_generation": ["build", "create", "implement", "generate code", "write code", "develop"],
    "deep_reasoning": ["analyze", "reason", "think", "plan", "strategy", "design"],
    "bug_detection": ["bug", "error", "issue", "problem", "fix bug", "crash"],
    "debugging": ["debug", "stack trace", "exception", "traceback", "fix error"],
    "code_review": ["review", "pr", "pull request", "quality", "check code"],
    "test_writing": ["test", "unit test", "integration test", "write test"],
    "testing_qa": ["qa", "quality assurance", "e2e", "end to end"],
    "refactoring": ["refactor", "clean up", "improve code", "restructure"],
    "frontend_react": ["react", "next.js", "vue", "svelte", "component"],
    "frontend_ui": ["html", "css", "ui", "interface", "design"],
    "website_builder": ["website", "landing page", "web page", "site"],
    "app_builder": ["app", "application", "mobile app"],
    "backend_api": ["api", "rest", "graphql", "fastapi", "backend", "server"],
    "api_development": ["express", "node", "endpoint", "route"],
    "database_sql": ["database", "sql", "postgres", "mongodb", "migration"],
    "data_analysis": ["analyze data", "pandas", "numpy", "jupyter", "analytics"],
    "devops_deployment": ["docker", "kubernetes", "deploy", "ci/cd", "aws", "gcp"],
    "git_operations": ["git", "commit", "branch", "merge", "pull", "push"],
    "security_audit": ["security", "vulnerability", "audit", "hack"],
    "documentation": ["doc", "readme", "comment", "manual"],
    "natural_language": ["chat", "nlp", "text", "summarize", "translate"],
    "multi_modal": ["image", "vision", "video", "audio", "multimodal"],
    "mobile_development": ["ios", "android", "react native", "flutter"],
    "ml_ai_tasks": ["machine learning", "ml", "ai", "train", "model"],
    "performance_opt": ["performance", "optimize", "speed", "benchmark"],
    "architecture_design": ["architecture", "system design", "microservice"],
    "reasoning_planning": ["reasoning", "planning", "strategy", "task breakdown"],
    "fast_response": ["quick", "simple", "fast", "hello", "hi"],
    "agentic_tasks": ["search", "browse", "web", "research", "agent"],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_task_type(goal: str) -> str:
    """Detect task type from goal text using keywords."""
    goal_lower = goal.lower()

    # Check each task type's keywords
    for task_type, keywords in TASK_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in goal_lower:
                return task_type

    # Default fallback
    return "code_generation"


def get_model_for_task(task_type: str, available_models: List[str] = None) -> Dict[str, Any]:
    """
    Get the best model for a task type.

    Args:
        task_type: The type of task (from TASK_CATEGORIES)
        available_models: Optional list of available models (for filtering)

    Returns:
        Dict with 'primary', 'fallback', 'roles', 'description'
    """
    if task_type in TASK_CATEGORIES:
        return TASK_CATEGORIES[task_type]

    # Default to code generation
    return TASK_CATEGORIES["code_generation"]


def get_role_model(role: str) -> Dict[str, Any]:
    """Get the optimal model configuration for an agent role."""
    if role in MODEL_ROLES:
        return MODEL_ROLES[role]

    # Default to coder role
    return MODEL_ROLES["coder"]
