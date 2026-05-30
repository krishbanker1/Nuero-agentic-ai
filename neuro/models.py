# Neuro Model Registry - 56 Models (Free Tier)
# Task-to-Model Assignment with 20 Categories - Optimized to beat Kimi 2.6, Manus 1.6, Claude Code, Codex
# Last saved: 2026-05-29

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
    'gemini', 'groq', 'openrouter', 'together', 'huggingface', 
    'cloudflare', 'cohere', 'lepton', 'mistral', 'perplexity'
})

# All 50+ models with structured metadata
MODEL_REGISTRY: List[ModelMetadata] = [
    # =============================================================================
    # GEMINI MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="gemini/gemini-3.5-flash",
        provider="gemini",
        roles=["planner", "architect", "coder", "validator"],
        strengths=["fast", "reasoning", "long-context", "code"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash",
        provider="gemini",
        roles=["planner", "coder", "debugger"],
        strengths=["fast", "code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash-lite",
        provider="gemini",
        roles=["coder", "frontend"],
        strengths=["fast", "cheap"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-3.1-flash-lite",
        provider="gemini",
        roles=["coder"],
        strengths=["fast", "cheap"],
        priority=4,
        fallback_priority=5,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash",
        provider="gemini",
        roles=["planner", "architect", "debugger"],
        strengths=["reasoning", "long-context"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    
    # =============================================================================
    # GEMINI MODELS (10 models)
    # =============================================================================
    ModelMetadata(
        name="gemini/gemini-3.5-flash",
        provider="gemini",
        roles=["code_generator", "frontend", "debugger", "general", "reasoning"],
        strengths=["fast", "coding", "reasoning", "multimodal", "vision"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-3.1-flash-lite",
        provider="gemini",
        roles=["frontend", "general", "analyzer"],
        strengths=["fast", "long-context", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash",
        provider="gemini",
        roles=["code_generator", "frontend", "debugger", "general", "reasoning"],
        strengths=["fast", "coding", "reasoning", "multimodal", "vision"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash-lite",
        provider="gemini",
        roles=["frontend", "general"],
        strengths=["very-fast", "free", "vision"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash",
        provider="gemini",
        roles=["code_generator", "debugger", "general"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash-lite",
        provider="gemini",
        roles=["frontend", "general"],
        strengths=["very-fast", "free", "lightweight"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash-001",
        provider="gemini",
        roles=["code_generator", "debugger"],
        strengths=["fast", "versioned"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash-lite-001",
        provider="gemini",
        roles=["frontend", "general"],
        strengths=["fast", "lite"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini/gemini-3.5-flash-latest",
        provider="gemini",
        roles=["code_generator", "debugger", "general"],
        strengths=["fast", "alias", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
    ),
    ModelMetadata(
        name="gemini/gemini/gemini-3.5-flash-lite-latest",
        provider="gemini",
        roles=["frontend", "general"],
        strengths=["fast", "lite", "alias", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1048576,
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
        name="groq/openai/gpt-oss-120b",
        provider="openrouter",
        roles=["architect", "planner", "reviewer"],
        strengths=["reasoning", "complex-tasks", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=200000,
    ),
    # NEW: DeepSeek V3 - Top free reasoning model (39.8% on SWE-bench)
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


# Task-to-Model Assignment with 20 Categories
# =============================================================================
# TESTED WORKING MODELS (2026-05-29)
# =============================================================================
# GEMINI (3 working, 1 quota-exhausted but will reset):
#   ✅ gemini/gemini-3.5-flash - Best coding + reasoning + multimodal
#   ✅ gemini/gemini-2.5-flash - Great price-performance
#   ✅ gemini/gemini-2.5-flash-lite - Fastest, cheapest
#   ⏳ gemini/gemini-2.0-flash - Quota will reset soon
#
# GROQ (ALL WORKING):
#   ✅ groq/openai/gpt-oss-120b - Best for complex reasoning, code review, architecture
#   ✅ groq/openai/gpt-oss-20b - Fast, good for reasoning
#   ✅ groq/qwen/qwen3-32b - Specialized coder, debugging, test writing
#   ✅ groq/llama-3.3-70b-versatile - Fast large model, general tasks
#   ✅ groq/llama-3.1-8b-instant - Ultra fast, quick tasks
#   ✅ groq/groq/compound - Agentic with built-in tools
#   ✅ groq/groq/compound-mini - Light agentic version

TASK_CATEGORIES = {
    # =============================================================================
    # TASK CATEGORIES - Assigned based on actual model capabilities
    # =============================================================================
    
    # 1. CODE GENERATION - GPT-OSS 120B (best for complex code) + Qwen (coding specialized)
    "code_generation": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["groq/qwen/qwen3-32b", "gemini/gemini-3.5-flash"],
        "roles": ["coder", "planner"],
        "description": "Full app/feature implementation"
    },
    
    # 2. DEEP REASONING - GPT-OSS 120B (complex reasoning)
    "deep_reasoning": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["groq/openai/gpt-oss-20b", "gemini/gemini-3.5-flash"],
        "roles": ["planner", "architect"],
        "description": "Complex reasoning, planning, analysis"
    },
    
    # 3. BUG DETECTION / DEBUGGING - Qwen3-32B (coding specialized)
    "bug_detection": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/openai/gpt-oss-120b"],
        "roles": ["debugger", "coder"],
        "description": "Bug finding and diagnosis"
    },
    "debugging": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/openai/gpt-oss-120b"],
        "roles": ["debugger", "coder"],
        "description": "Error fixing, stack trace analysis"
    },
    
    # 4. CODE REVIEW - GPT-OSS 120B (complex analysis)
    "code_review": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["groq/openai/gpt-oss-20b", "gemini/gemini-3.5-flash"],
        "roles": ["reviewer", "architect"],
        "description": "PR reviews, quality assessment"
    },
    
    # 5. TEST WRITING / TESTING_QA - Qwen3-32B (coding specialized)
    "test_writing": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-3.5-flash"],
        "roles": ["validator", "coder"],
        "description": "Unit tests, integration tests"
    },
    "testing_qa": {
        "primary": "groq/qwen/qwen3-32b",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-3.5-flash"],
        "roles": ["validator", "coder"],
        "description": "QA automation, E2E tests"
    },
    
    # 6. REFACTORING - Gemini 3.5 Flash (coding expert)
    "refactoring": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "groq/qwen/qwen3-32b"],
        "roles": ["refactor", "reviewer"],
        "description": "Code restructuring, optimization"
    },
    "code_refactoring": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "groq/qwen/qwen3-32b"],
        "roles": ["refactor", "reviewer"],
        "description": "Code improvement, pattern application"
    },
    
    # 7. FAST RESPONSE - Gemini 2.5 Flash-Lite (fastest, cheapest)
    "fast_response": {
        "primary": "gemini/gemini-2.5-flash-lite",
        "fallback": ["groq/llama-3.1-8b-instant", "gemini/gemini-2.5-flash"],
        "roles": ["coder"],
        "description": "Quick answers, simple tasks - Lite is fastest"
    },
    "code_completion": {
        "primary": "gemini/gemini-2.5-flash-lite",
        "fallback": ["groq/llama-3.1-8b-instant", "gemini/gemini-2.5-flash"],
        "roles": ["coder"],
        "description": "Autocomplete, snippet generation"
    },
    
    # 8. LONG CONTEXT - Gemini 3.5 Flash (1M token context)
    "long_context": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["gemini/gemini-2.5-flash", "groq/openai/gpt-oss-120b"],
        "roles": ["architect", "planner"],
        "description": "Large codebase, 1M+ context"
    },
    
    # 9. BACKEND_API - Gemini 3.5 Flash (coding + agentic)
    "backend_api": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-2.5-flash"],
        "roles": ["coder", "architect"],
        "description": "REST, GraphQL, FastAPI, backend logic"
    },
    "api_development": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-2.5-flash"],
        "roles": ["coder", "architect"],
        "description": "API design, Express, Node.js"
    },
    
    # 10. FRONTEND_REACT - Gemini 3.5 Flash (multimodal, coding)
    "frontend_react": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-2.5-flash"],
        "roles": ["frontend", "coder"],
        "description": "React, Next.js, Vue, Svelte"
    },
    "frontend_ui": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["gemini/gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["frontend", "coder"],
        "description": "HTML/CSS, UI components"
    },
    
    # 11. DATABASE_SQL - Gemini 3.5 Flash (schema design)
    "database_sql": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "groq/llama-3.3-70b-versatile"],
        "roles": ["coder", "architect"],
        "description": "SQL, PostgreSQL, MongoDB, migrations"
    },
    
    # 12. DEVOPS_DEPLOYMENT - GPT-OSS 120B (complex planning)
    "devops_deployment": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["coder", "architect"],
        "description": "Docker, K8s, CI/CD, AWS, GCP"
    },
    
    # 13. SECURITY_AUDIT - GPT-OSS 120B (thorough analysis)
    "security_audit": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["groq/openai/gpt-oss-20b", "gemini/gemini-3.5-flash"],
        "roles": ["reviewer", "debugger"],
        "description": "Vulnerability scanning, fixes"
    },
    
    # 14. DOCUMENTATION - Gemini 2.5 Flash (great writer)
    "documentation": {
        "primary": "gemini/gemini-2.5-flash",
        "fallback": ["gemini/gemini-3.5-flash", "groq/llama-3.1-8b-instant"],
        "roles": ["documentation"],
        "description": "README, API docs, comments"
    },
    
    # 15. DATA_ANALYSIS - Gemini 3.5 Flash (coding + reasoning)
    "data_analysis": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "groq/llama-3.3-70b-versatile"],
        "roles": ["coder", "planner"],
        "description": "Pandas, NumPy, analytics, Jupyter"
    },
    
    # 16. MOBILE_DEVELOPMENT - Gemini 3.5 Flash (coding expert)
    "mobile_development": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/openai/gpt-oss-120b", "gemini/gemini-2.5-flash"],
        "roles": ["frontend", "coder"],
        "description": "iOS, Android, React Native, Flutter"
    },
    
    # 17. ML_AI_TASKS - GPT-OSS 120B (complex ML reasoning)
    "ml_ai_tasks": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["coder", "planner"],
        "description": "ML pipelines, AI training"
    },
    
    # 18. PERFORMANCE_OPT - GPT-OSS 120B (complex analysis)
    "performance_opt": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/qwen/qwen3-32b"],
        "roles": ["debugger", "refactor"],
        "description": "Profiling, caching, optimization"
    },
    "performance_optimization": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/qwen/qwen3-32b"],
        "roles": ["debugger", "refactor"],
        "description": "Performance tuning, benchmarks"
    },
    
    # 19. GIT_OPERATIONS - Groq 8B (quick commands)
    "git_operations": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": ["gemini/gemini-2.5-flash-lite", "gemini/gemini-2.5-flash"],
        "roles": ["coder"],
        "description": "Git commands, PRs, merges"
    },
    
    # 20. ARCHITECTURE_DESIGN - GPT-OSS 120B (system design)
    "architecture_design": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["architect", "planner"],
        "description": "System design, microservices, patterns"
    },
    
    # 21. NATURAL_LANGUAGE - Gemini 3.5 Flash (multimodal)
    "natural_language": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["gemini/gemini-2.5-flash", "groq/llama-3.1-8b-instant"],
        "roles": ["planner"],
        "description": "Chatbots, summarization, NLP"
    },
    "office_document_generation": {
        "primary": "gemini/gemini-2.5-flash",
        "fallback": ["gemini/gemini-3.5-flash", "gemini/gemini-2.5-flash-lite"],
        "roles": ["planner"],
        "description": "Word, Excel, PowerPoint generation"
    },
    
    # 22. MULTI_MODAL - Gemini 3.5 Flash (vision + text)
    "multi_modal": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["gemini/gemini-2.5-flash", "groq/llama-3.3-70b-versatile"],
        "roles": ["frontend", "coder"],
        "description": "Image understanding, file processing"
    },
    
    # 23. REASONING_PLANNING - GPT-OSS 120B (complex planning)
    "reasoning_planning": {
        "primary": "groq/openai/gpt-oss-120b",
        "fallback": ["gemini/gemini-3.5-flash", "groq/openai/gpt-oss-20b"],
        "roles": ["planner", "architect"],
        "description": "Strategic planning, task decomposition"
    },
}

MODEL_ROLES = {
    "executor": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/qwen/qwen3-coder:free", "groq/llama-3.3-70b-versatile"],
        "temperature": 0.1,
        "max_tokens": 8192,
    },
    "planner": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/google/gemma-4-31b-it:free", "gemini/gemini-3.5-flash"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    "debugger": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["huggingface/WizardCoder-33B", "groq/qwen/qwen3-32b"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
    "reviewer": {
        "primary": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
}