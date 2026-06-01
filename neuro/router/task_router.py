"""
Neuro Model Assignment - Task-to-Model Routing

Based on comprehensive model assignment sheet with 50+ roles.
Each role has primary and fallback models for optimal task routing.

Usage:
    from neuro.router.task_router import get_model_for_role, classify_task
    
    model = get_model_for_role("Frontend Coder")
    task_type = classify_task("Build a React login page")
"""

from __future__ import annotations

from typing import List, Dict, Tuple, Any
from enum import Enum
import random


class TaskRole(Enum):
    """All available task roles in Neuro."""
    # Planning & Analysis
    INTENT_ROUTER = "intent_router"
    TASK_CLASSIFIER = "task_classifier"
    COMPLEXITY_ESTIMATOR = "complexity_estimator"
    MAIN_PLANNER = "main_planner"
    LONG_HORIZON_PLANNER = "long_horizon_planner"
    PRODUCT_MANAGER = "product_manager"
    
    # Research
    RESEARCH_AGENT = "research_agent"
    BROWSER_AGENT = "browser_agent"
    GITHUB_REPO_SCOUT = "github_repo_scout"
    
    # Architecture
    SYSTEM_ARCHITECT = "system_architect"
    BACKEND_ARCHITECT = "backend_architect"
    FRONTEND_ARCHITECT = "frontend_architect"
    DATABASE_ARCHITECT = "database_architect"
    API_CONTRACT_WRITER = "api_contract_writer"
    
    # Task Decomposition
    TASK_DECOMPOSER = "task_decomposer"
    TICKET_GENERATOR = "ticket_generator"
    EXECUTOR_CONTROLLER = "executor_controller"
    
    # Code Execution
    FILE_INSPECTOR = "file_inspector"
    FRONTEND_CODER = "frontend_coder"
    BACKEND_CODER = "backend_coder"
    FULL_STACK_CODER = "full_stack_coder"
    DATABASE_CODER = "database_coder"
    AUTH_CODER = "auth_coder"
    INTEGRATION_CODER = "integration_coder"
    AGENTIC_CODER = "agentic_coder"
    SMALL_PATCH_CODER = "small_patch_coder"
    REFACTOR_AGENT = "refactor_agent"
    TERMINAL_EXECUTOR = "terminal_executor"
    
    # Debugging
    LOG_COMPRESSOR = "log_compressor"
    DEBUGGER = "debugger"
    FRONTEND_DEBUGGER = "frontend_debugger"
    BACKEND_DEBUGGER = "backend_debugger"
    DATABASE_DEBUGGER = "database_debugger"
    DEPENDENCY_DEBUGGER = "dependency_debugger"
    
    # Validation
    VALIDATOR = "validator"
    TYPECHECK_VALIDATOR = "typecheck_validator"
    BUILD_VALIDATOR = "build_validator"
    API_VALIDATOR = "api_validator"
    UI_VALIDATOR = "ui_validator"
    
    # Review
    SECURITY_REVIEWER = "security_reviewer"
    ENTERPRISE_CRITIC = "enterprise_critic"
    PERFORMANCE_AGENT = "performance_agent"
    TESTING_AGENT = "testing_agent"
    SELF_HEALING_AGENT = "self_healing_agent"
    
    # Design
    UI_DESIGNER = "ui_designer"
    UX_FLOW_DESIGNER = "ux_flow_designer"
    CSS_TAILWIND_FIXER = "css_tailwind_fixer"
    VISION_REVIEWER = "vision_reviewer"
    
    # Documentation
    PRESENTATION_BUILDER = "presentation_builder"
    DOCUMENT_WRITER = "document_writer"
    MARKETING_WRITER = "marketing_writer"
    
    # Memory & Utilities
    MEMORY_SUMMARIZER = "memory_summarizer"
    EMBEDDING_AGENT = "embedding_agent"
    SPEECH_STT_AGENT = "speech_stt_agent"
    TOOL_CALLING_AGENT = "tool_calling_agent"
    STRUCTURED_JSON_AGENT = "structured_json_agent"
    FINAL_ORCHESTRATOR = "final_orchestrator"


class Provider(Enum):
    """API Providers."""
    GROQ = "groq"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    SAMBANOVA = "sambanova"
    CEREBRAS = "cerebras"
    CLOUDFLARE = "cloudflare"
    HUGGINGFACE = "huggingface"


# ============================================================================
# MODEL REGISTRY - All available models organized by provider
# ============================================================================

PROVIDER_MODELS = {
    # Groq - Fast inference, good for routing/classifier tasks
    # FROM YOUR INSTRUCTIONS: llama-3.1-8b-instant, llama-3.3-70b-versatile, qwen/qwen3-coder:free, openai/gpt-oss-120b, moonshotai/kimi-k2-instruct
    Provider.GROQ: [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "qwen/qwen3-coder:free",
        "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct",
    ],
    
    # Google Gemini API - native IDs only, no OpenRouter prefixes.
    Provider.GOOGLE: [
        "gemini-3.5-flash",
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-image",
        "gemini-embedding-2",
        "gemini-embedding-2",
    ],
    
    # OpenRouter FREE - Best for coding, reasoning, agentic tasks
    # FROM YOUR INSTRUCTIONS: free, owl-alpha, qwen/qwen3-coder:free, nvidia/nemotron-3-super-120b-a12b:free,
    # nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free, poolside/laguna-m.1:free, poolside/laguna-xs.2:free,
    # baidu/cobuddy:free, google/gemma-4-31b-it:free, google/gemma-4-26b-a4b-it:free,
    # meta-llama/llama-3.3-70b-instruct:free, meta-llama/llama-3.3-70b-instruct:free,
    # NOTE: deepseek/deepseek-chat used in roles but may be SambaNova or paid OpenRouter
    Provider.OPENROUTER: [
        "free",
        "owl-alpha",
        "qwen/qwen3-coder:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "poolside/laguna-m.1:free",
        "poolside/laguna-xs.2:free",
        "baidu/cobuddy:free",
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "liquid/lfm-2.5-1.2b-thinking:free",
        "z-ai/glm-4.5-air:free",
        # Additional models used in role assignments (may be available on OpenRouter):
        "deepseek/deepseek-chat",
    ],
    
    # SambaNova - Serious fallback, backend, planning
    # FROM YOUR INSTRUCTIONS: deepseek-v3.1, deepseek-v3.2, gemma-3-12b-it, gpt-oss-120b, llama-4-maverick-17b-128e-instruct, meta-llama-3.3-70b-instruct, minimax-m2.7
    Provider.SAMBANOVA: [
        "deepseek-v3.1",
        "deepseek-v3.2",
        "gemma-3-12b-it",
        "gpt-oss-120b",
        "llama-4-maverick-17b-128e-instruct",
        "meta-llama-3.3-70b-instruct",
        "minimax-m2.7",
    ],
    
    # Cerebras - Fast reasoning, agent loops
    # FROM YOUR INSTRUCTIONS: llama-3.3-70b, llama-3.1-8b, qwen-3-32b, qwen-3-235b, gpt-oss-120b
    Provider.CEREBRAS: [
        "llama-3.3-70b",
        "llama-3.1-8b",
        "qwen-3-32b",
        "qwen-3-235b",
        "gpt-oss-120b",
    ],
    
    # Cloudflare - Edge tools, embeddings, ASR, vision
    # FROM YOUR INSTRUCTIONS: kimi-k2.6, glm-4.7-flash, gpt-oss-120b, llama-4-scout, gemma models, BGE embedding models, Whisper/ASR models
    Provider.CLOUDFLARE: [
        "kimi-k2.6",
        "glm-4.7-flash",
        "gpt-oss-120b",
        "llama-4-scout",
        "@cf/meta/llama-3-70b-instruct-fp8-fast",  # Workers AI format
        "@cf/mistral/mistral-7b-instruct-v0.2",  # Workers AI format
    ],
    
    # HuggingFace - Niche fallback, embeddings, ASR, vision
    # FROM YOUR INSTRUCTIONS: BGE/E5 embedding models, Whisper ASR models, image/vision specialist models, small open instruct models
    Provider.HUGGINGFACE: [
        "BGE/E5-embedding-models",
        "Whisper-ASR-models",
        "image-vision-specialist-models",
        "small-open-instruct-models",
    ],
}


# ============================================================================
# TASK-TO-MODEL ROUTING TABLE
# Each role has primary models (in order of preference) and fallback models
# ============================================================================

ROLE_MODEL_ROUTING: Dict[TaskRole, Dict[str, List[Tuple[Provider, str]]]] = {
    # -------------------------------------------------------------------------
    # Planning & Analysis Roles
    # -------------------------------------------------------------------------
    TaskRole.INTENT_ROUTER: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
        ],
        "fallback": [
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.TASK_CLASSIFIER: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GROQ, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.COMPLEXITY_ESTIMATOR: {
        "primary": [
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
        ],
    },
    
    TaskRole.MAIN_PLANNER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
        ],
    },
    
    TaskRole.LONG_HORIZON_PLANNER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "qwen/qwen3-235b"),
        ],
    },
    
    TaskRole.PRODUCT_MANAGER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Research Roles
    # -------------------------------------------------------------------------
    TaskRole.RESEARCH_AGENT: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.1"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.BROWSER_AGENT: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.GITHUB_REPO_SCOUT: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Architecture Roles
    # -------------------------------------------------------------------------
    TaskRole.SYSTEM_ARCHITECT: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
        ],
        "fallback": [
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    TaskRole.BACKEND_ARCHITECT: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "llama-4-maverick-17b-128e-instruct"),
        ],
    },
    
    TaskRole.FRONTEND_ARCHITECT: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        ],
    },
    
    TaskRole.DATABASE_ARCHITECT: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    TaskRole.API_CONTRACT_WRITER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Task Decomposition Roles
    # -------------------------------------------------------------------------
    TaskRole.TASK_DECOMPOSER: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
    },
    
    TaskRole.TICKET_GENERATOR: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
    },
    
    TaskRole.EXECUTOR_CONTROLLER: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Coding Roles - core repair and build roles
    # -------------------------------------------------------------------------
    TaskRole.FILE_INSPECTOR: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.FRONTEND_CODER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
    },
    
    TaskRole.BACKEND_CODER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    TaskRole.FULL_STACK_CODER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
        ],
    },
    
    TaskRole.DATABASE_CODER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.AUTH_CODER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
        ],
    },
    
    TaskRole.INTEGRATION_CODER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.AGENTIC_CODER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
    },
    
    TaskRole.SMALL_PATCH_CODER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.REFACTOR_AGENT: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
        ],
    },
    
    TaskRole.TERMINAL_EXECUTOR: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Debugging Roles
    # -------------------------------------------------------------------------
    TaskRole.LOG_COMPRESSOR: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
        ],
        "fallback": [
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.DEBUGGER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
        ],
    },
    
    TaskRole.FRONTEND_DEBUGGER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
    },
    
    TaskRole.BACKEND_DEBUGGER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
        ],
    },
    
    TaskRole.DATABASE_DEBUGGER: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
        "fallback": [
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.DEPENDENCY_DEBUGGER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Validation Roles
    # -------------------------------------------------------------------------
    TaskRole.VALIDATOR: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.TYPECHECK_VALIDATOR: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
    },
    
    TaskRole.BUILD_VALIDATOR: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.API_VALIDATOR: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.UI_VALIDATOR: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "free"),
            (Provider.CLOUDFLARE, "vision-models"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Review Roles
    # -------------------------------------------------------------------------
    TaskRole.SECURITY_REVIEWER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
        ],
    },
    
    TaskRole.ENTERPRISE_CRITIC: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    TaskRole.PERFORMANCE_AGENT: {
        "primary": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.TESTING_AGENT: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.SELF_HEALING_AGENT: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Design Roles
    # -------------------------------------------------------------------------
    TaskRole.UI_DESIGNER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "free"),
            (Provider.OPENROUTER, "z-ai/glm-4.5-air:free"),
        ],
    },
    
    TaskRole.UX_FLOW_DESIGNER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.CSS_TAILWIND_FIXER: {
        "primary": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.VISION_REVIEWER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.CLOUDFLARE, "kimi-k2.6"),
            (Provider.OPENROUTER, "z-ai/glm-4.5-air:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Documentation Roles
    # -------------------------------------------------------------------------
    TaskRole.PRESENTATION_BUILDER: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
        ],
    },
    
    TaskRole.DOCUMENT_WRITER: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.MARKETING_WRITER: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
    
    # -------------------------------------------------------------------------
    # Memory & Utility Roles
    # -------------------------------------------------------------------------
    TaskRole.MEMORY_SUMMARIZER: {
        "primary": [
            (Provider.GROQ, "llama-3.1-8b-instant"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.EMBEDDING_AGENT: {
        "primary": [
            (Provider.GOOGLE, "gemini-embedding-2"),
            (Provider.CLOUDFLARE, "BGE-embedding-models"),
            (Provider.HUGGINGFACE, "BGE/E5-embedding-models"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.SPEECH_STT_AGENT: {
        "primary": [
            (Provider.GROQ, "STT/Whisper-model"),
            (Provider.CLOUDFLARE, "Whisper-ASR-models"),
            (Provider.HUGGINGFACE, "Whisper-ASR-models"),
        ],
        "fallback": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
        ],
    },
    
    TaskRole.TOOL_CALLING_AGENT: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
        ],
        "fallback": [
            (Provider.GROQ, "llama-3.3-70b-versatile"),
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.STRUCTURED_JSON_AGENT: {
        "primary": [
            (Provider.GOOGLE, "gemini-2.5-flash"),
            (Provider.GOOGLE, "gemini-2.0-flash-lite"),
            (Provider.GROQ, "llama-3.1-8b-instant"),
        ],
        "fallback": [
            (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
            (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
            (Provider.OPENROUTER, "free"),
        ],
    },
    
    TaskRole.FINAL_ORCHESTRATOR: {
        "primary": [
            (Provider.GOOGLE, "gemini-3.5-flash"),
            (Provider.OPENROUTER, "owl-alpha"),
            (Provider.GOOGLE, "gemini-3-flash-preview"),
        ],
        "fallback": [
            (Provider.GROQ, "openai/gpt-oss-120b"),
            (Provider.SAMBANOVA, "deepseek-v3.2"),
            (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"),
        ],
    },
}


# ============================================================================
# TASK CLASSIFICATION - Map keywords to roles
# ============================================================================

TASK_KEYWORDS = {
    TaskRole.RESEARCH_AGENT: [
        "research", "search", "find", "lookup", "web", "docs", "documentation"
    ],
    TaskRole.BROWSER_AGENT: [
        "browse", "scrape", "read website", "fetch url"
    ],
    TaskRole.GITHUB_REPO_SCOUT: [
        "compare repo", "compare framework", "github", "repository"
    ],
    TaskRole.SYSTEM_ARCHITECT: [
        "architecture", "stack", "design system", "system design"
    ],
    TaskRole.BACKEND_ARCHITECT: [
        "backend design", "api design", "service design"
    ],
    TaskRole.FRONTEND_ARCHITECT: [
        "frontend design", "ui design", "component structure"
    ],
    TaskRole.DATABASE_ARCHITECT: [
        "database design", "schema", "data model"
    ],
    TaskRole.API_CONTRACT_WRITER: [
        "api contract", "openapi", "swagger", "api routes"
    ],
    TaskRole.FRONTEND_CODER: [
        "react", "next", "vue", "angular", "svelte", "html", "css", "tailwind"
    ],
    TaskRole.BACKEND_CODER: [
        "backend", "server", "api", "express", "fastapi", "django", "flask"
    ],
    TaskRole.FULL_STACK_CODER: [
        "full stack", "end to end", "complete feature"
    ],
    TaskRole.DATABASE_CODER: [
        "database", "sql", "prisma", "drizzle", "migration"
    ],
    TaskRole.AUTH_CODER: [
        "auth", "login", "jwt", "oauth", "session", "rbac", "permission"
    ],
    TaskRole.INTEGRATION_CODER: [
        "integration", "oauth", "webhook", "third party"
    ],
    TaskRole.AGENTIC_CODER: [
        "autonomous", "agent", "repo editing", "self directed"
    ],
    TaskRole.SMALL_PATCH_CODER: [
        "bug fix", "patch", "tiny", "small fix", "hotfix"
    ],
    TaskRole.REFACTOR_AGENT: [
        "refactor", "clean up", "restructure", "improve code"
    ],
    TaskRole.TERMINAL_EXECUTOR: [
        "terminal", "command", "bash", "shell", "cli"
    ],
    TaskRole.DEBUGGER: [
        "debug", "fix error", "error", "exception", "crash"
    ],
    TaskRole.FRONTEND_DEBUGGER: [
        "frontend bug", "ui bug", "css bug", "react bug"
    ],
    TaskRole.BACKEND_DEBUGGER: [
        "backend bug", "server error", "api error", "500"
    ],
    TaskRole.DATABASE_DEBUGGER: [
        "database bug", "query error", "migration error"
    ],
    TaskRole.DEPENDENCY_DEBUGGER: [
        "dependency", "package", "npm", "pip", "import error", "version"
    ],
    TaskRole.VALIDATOR: [
        "validate", "test", "verify", "check"
    ],
    TaskRole.TYPECHECK_VALIDATOR: [
        "typecheck", "typescript", "mypy", "type error"
    ],
    TaskRole.BUILD_VALIDATOR: [
        "build", "compile", "lint", "format"
    ],
    TaskRole.API_VALIDATOR: [
        "api test", "endpoint test", "smoke test"
    ],
    TaskRole.UI_VALIDATOR: [
        "ui test", "visual", "screenshot", "e2e"
    ],
    TaskRole.SECURITY_REVIEWER: [
        "security", "vulnerability", "injection", "xss", "csrf"
    ],
    TaskRole.ENTERPRISE_CRITIC: [
        "review", "quality", "scalability", "enterprise"
    ],
    TaskRole.PERFORMANCE_AGENT: [
        "performance", "optimize", "speed", "latency"
    ],
    TaskRole.TESTING_AGENT: [
        "test", "unit test", "integration test", "e2e test"
    ],
    TaskRole.SELF_HEALING_AGENT: [
        "self heal", "auto fix", "retry", "recover"
    ],
    TaskRole.UI_DESIGNER: [
        "design", "ui", "visual", "polish"
    ],
    TaskRole.UX_FLOW_DESIGNER: [
        "ux", "user flow", "journey", "experience"
    ],
    TaskRole.CSS_TAILWIND_FIXER: [
        "css", "tailwind", "styling", "responsive", "layout"
    ],
    TaskRole.VISION_REVIEWER: [
        "screenshot", "visual", "design review", "ui review"
    ],
    TaskRole.PRESENTATION_BUILDER: [
        "presentation", "slides", "deck", "ppt"
    ],
    TaskRole.DOCUMENT_WRITER: [
        "document", "readme", "guide", "docs"
    ],
    TaskRole.MARKETING_WRITER: [
        "marketing", "landing", "copy", "launch"
    ],
    TaskRole.MEMORY_SUMMARIZER: [
        "summarize", "memory", "context"
    ],
    TaskRole.MAIN_PLANNER: [
        "plan", "architecture", "build"
    ],
    TaskRole.LONG_HORIZON_PLANNER: [
        "roadmap", "multi-stage", "enterprise build"
    ],
    TaskRole.PRODUCT_MANAGER: [
        "prd", "mvp", "feature scope", "product"
    ],
    TaskRole.TASK_DECOMPOSER: [
        "decompose", "break down", "ticket"
    ],
}


# ============================================================================
# FUNCTIONS
# ============================================================================

def classify_task(task_description: str) -> TaskRole:
    """
    Classify a task description into a TaskRole based on keywords.
    
    Args:
        task_description: Natural language description of the task
        
    Returns:
        TaskRole enum value representing the best role for this task
    """
    task_lower = task_description.lower()
    
    # Score each role based on keyword matches
    scores: Dict[TaskRole, int] = {}
    
    for role, keywords in TASK_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in task_lower)
        if score > 0:
            scores[role] = score
    
    if not scores:
        # Default fallback for unknown tasks
        return TaskRole.INTENT_ROUTER
    
    # Return the role with highest score
    return max(scores, key=scores.get)



# Balanced production routing overrides. These keep coding/debugging ownership on
# Qwen/DeepSeek/OpenRouter while allowing native Google Gemini where it is strong.
def _balanced_route(primary: List[Tuple[Provider, str]], fallback: List[Tuple[Provider, str]]) -> Dict[str, List[Tuple[Provider, str]]]:
    return {"primary": primary, "fallback": fallback}

_FAST_ROLES = [
    TaskRole.INTENT_ROUTER, TaskRole.TASK_CLASSIFIER, TaskRole.COMPLEXITY_ESTIMATOR,
    TaskRole.LOG_COMPRESSOR, TaskRole.MEMORY_SUMMARIZER, TaskRole.STRUCTURED_JSON_AGENT,
]
_PLANNING_ROLES = [TaskRole.MAIN_PLANNER, TaskRole.LONG_HORIZON_PLANNER, TaskRole.PRODUCT_MANAGER, TaskRole.FINAL_ORCHESTRATOR]
_ARCHITECTURE_ROLES = [
    TaskRole.SYSTEM_ARCHITECT, TaskRole.BACKEND_ARCHITECT, TaskRole.FRONTEND_ARCHITECT,
    TaskRole.DATABASE_ARCHITECT, TaskRole.API_CONTRACT_WRITER,
]
_CODING_ROLES = [
    TaskRole.FRONTEND_CODER, TaskRole.BACKEND_CODER, TaskRole.FULL_STACK_CODER,
    TaskRole.DATABASE_CODER, TaskRole.AUTH_CODER, TaskRole.INTEGRATION_CODER,
    TaskRole.AGENTIC_CODER, TaskRole.SMALL_PATCH_CODER, TaskRole.REFACTOR_AGENT,
]
_DEBUG_ROLES = [
    TaskRole.DEBUGGER, TaskRole.FRONTEND_DEBUGGER, TaskRole.BACKEND_DEBUGGER,
    TaskRole.DATABASE_DEBUGGER, TaskRole.DEPENDENCY_DEBUGGER, TaskRole.SELF_HEALING_AGENT,
]
_VALIDATION_ROLES = [TaskRole.VALIDATOR, TaskRole.TYPECHECK_VALIDATOR, TaskRole.BUILD_VALIDATOR, TaskRole.API_VALIDATOR, TaskRole.TESTING_AGENT]
_REVIEW_ROLES = [TaskRole.SECURITY_REVIEWER, TaskRole.ENTERPRISE_CRITIC, TaskRole.PERFORMANCE_AGENT]

for _role in _FAST_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.GROQ, "llama-3.1-8b-instant"), (Provider.GOOGLE, "gemini-2.0-flash-lite")],
        [(Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.OPENROUTER, "free")],
    )

for _role in _PLANNING_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.GROQ, "openai/gpt-oss-120b"), (Provider.OPENROUTER, "owl-alpha")],
        [(Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.SAMBANOVA, "deepseek-v3.2"), (Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free")],
    )

for _role in _ARCHITECTURE_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.GROQ, "openai/gpt-oss-120b")],
        [(Provider.OPENROUTER, "qwen/qwen3-coder:free"), (Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.SAMBANOVA, "deepseek-v3.2")],
    )

for _role in _CODING_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.OPENROUTER, "qwen/qwen3-coder:free"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free")],
        [(Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GROQ, "qwen/qwen3-coder:free"), (Provider.GROQ, "llama-3.3-70b-versatile")],
    )

for _role in _DEBUG_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.OPENROUTER, "qwen/qwen3-coder:free")],
        [(Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.SAMBANOVA, "deepseek-v3.2")],
    )

for _role in _VALIDATION_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.OPENROUTER, "qwen/qwen3-coder:free"), (Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GROQ, "llama-3.3-70b-versatile")],
        [(Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.GROQ, "openai/gpt-oss-120b")],
    )

for _role in _REVIEW_ROLES:
    ROLE_MODEL_ROUTING[_role] = _balanced_route(
        [(Provider.GROQ, "openai/gpt-oss-120b"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"), (Provider.GOOGLE, "gemini-3.5-flash")],
        [(Provider.OPENROUTER, "qwen/qwen3-coder:free"), (Provider.SAMBANOVA, "deepseek-v3.2"), (Provider.GROQ, "llama-3.3-70b-versatile")],
    )

ROLE_MODEL_ROUTING.update({
    TaskRole.UI_DESIGNER: _balanced_route([(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.OPENROUTER, "qwen/qwen3-coder:free")], [(Provider.OPENROUTER, "z-ai/glm-4.5-air:free"), (Provider.CLOUDFLARE, "vision-models"), (Provider.GROQ, "llama-3.3-70b-versatile")]),
    TaskRole.UX_FLOW_DESIGNER: _balanced_route([(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.OPENROUTER, "qwen/qwen3-coder:free")], [(Provider.OPENROUTER, "z-ai/glm-4.5-air:free"), (Provider.GROQ, "llama-3.3-70b-versatile")]),
    TaskRole.CSS_TAILWIND_FIXER: _balanced_route([(Provider.OPENROUTER, "qwen/qwen3-coder:free"), (Provider.GOOGLE, "gemini-3.5-flash")], [(Provider.OPENROUTER, "z-ai/glm-4.5-air:free"), (Provider.GROQ, "llama-3.3-70b-versatile")]),
    TaskRole.VISION_REVIEWER: _balanced_route([(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.GOOGLE, "gemini-2.5-flash-image")], [(Provider.OPENROUTER, "z-ai/glm-4.5-air:free"), (Provider.CLOUDFLARE, "vision-models"), (Provider.GROQ, "llama-3.3-70b-versatile")]),
    TaskRole.PRESENTATION_BUILDER: _balanced_route([(Provider.GOOGLE, "gemini-3.5-flash"), (Provider.OPENROUTER, "qwen/qwen3-coder:free")], [(Provider.OPENROUTER, "z-ai/glm-4.5-air:free"), (Provider.GROQ, "llama-3.3-70b-versatile")]),
    TaskRole.DOCUMENT_WRITER: _balanced_route([(Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.GROQ, "openai/gpt-oss-120b")], [(Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free")]),
    TaskRole.MARKETING_WRITER: _balanced_route([(Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GROQ, "llama-3.3-70b-versatile"), (Provider.GROQ, "openai/gpt-oss-120b")], [(Provider.OPENROUTER, "meta-llama/llama-3.3-70b-instruct:free"), (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free")]),
    TaskRole.EMBEDDING_AGENT: _balanced_route([(Provider.GOOGLE, "gemini-embedding-2"), (Provider.GOOGLE, "gemini-embedding-2"), (Provider.CLOUDFLARE, "BGE-embedding-models")], [(Provider.HUGGINGFACE, "BGE/E5-embedding-models")]),
    TaskRole.SPEECH_STT_AGENT: _balanced_route([(Provider.GROQ, "whisper-large-v3"), (Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GOOGLE, "gemini-2.5-flash")], [(Provider.GOOGLE, "gemini-2.5-flash"), (Provider.GOOGLE, "gemini-2.5-flash"), (Provider.CLOUDFLARE, "whisper-asr"), (Provider.HUGGINGFACE, "whisper-asr")]),
})

def get_model_for_role(
    role: TaskRole,
    prefer_fallback: bool = False,
    randomize: bool = True
) -> Tuple[Provider, str]:
    """
    Get the best model for a given task role.
    
    Args:
        role: TaskRole enum value
        prefer_fallback: If True, start from fallback models
        randomize: If True, randomize within model tier
        
    Returns:
        Tuple of (Provider, model_name)
    """
    routing = ROLE_MODEL_ROUTING.get(role)
    if not routing:
        # Default fallback
        return (Provider.GROQ, "llama-3.1-8b-instant")
    
    model_list = routing["fallback"] if prefer_fallback else routing["primary"]
    
    if not model_list:
        return (Provider.GROQ, "llama-3.1-8b-instant")
    
    if randomize and len(model_list) > 1:
        # Add some randomness to distribute load
        return random.choice(model_list[:3])  # Pick from top 3
    
    return model_list[0]


def get_model_chain(
    role: TaskRole,
    max_models: int = 3
) -> List[Tuple[Provider, str]]:
    """
    Get a chain of models for a role (primary + fallback).
    
    Args:
        role: TaskRole enum value
        max_models: Maximum number of models to return
        
    Returns:
        List of (Provider, model_name) tuples
    """
    routing = ROLE_MODEL_ROUTING.get(role)
    if not routing:
        return [(Provider.GROQ, "llama-3.1-8b-instant")]
    
    chain = routing["primary"] + routing["fallback"]
    return chain[:max_models]


def get_models_for_provider(provider: Provider) -> List[str]:
    """Get all models available for a provider."""
    return PROVIDER_MODELS.get(provider, [])


def is_free_model(model_name: str) -> bool:
    """Check if a model is free (no cost)."""
    return ":free" in model_name or "free" in model_name


def get_best_free_model() -> Tuple[Provider, str]:
    """Get the best free model for coding tasks."""
    return (Provider.OPENROUTER, "qwen/qwen3-coder:free")


def get_model_info(role: TaskRole) -> Dict[str, Any]:
    """Get detailed info about models for a role."""
    routing = ROLE_MODEL_ROUTING.get(role)
    if not routing:
        return {"error": f"Unknown role: {role}"}
    
    return {
        "role": role.value,
        "primary": [
            f"{p.value}/{m}" for p, m in routing["primary"]
        ],
        "fallback": [
            f"{p.value}/{m}" for p, m in routing["fallback"]
        ],
        "has_free_models": any(
            is_free_model(m) for _, m in routing["primary"] + routing["fallback"]
        ),
    }


# ============================================================================
# EXACT CHAINS FOR COMMON TASKS
# ============================================================================

TASK_CHAINS = {
    "quick_routing": [
        (Provider.GROQ, "llama-3.1-8b-instant"),
        (Provider.GOOGLE, "gemini-2.0-flash-lite"),
        (Provider.GOOGLE, "gemini-2.0-flash-lite"),
        (Provider.OPENROUTER, "free"),
    ],
    "hard_planning": [
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.OPENROUTER, "owl-alpha"),
        (Provider.GROQ, "openai/gpt-oss-120b"),
        (Provider.SAMBANOVA, "deepseek-v3.2"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ],
    "app_architecture": [
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.OPENROUTER, "owl-alpha"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.GROQ, "openai/gpt-oss-120b"),
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
    ],
    "frontend_coding": [
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        (Provider.OPENROUTER, "poolside/laguna-m.1:free"),
        (Provider.OPENROUTER, "poolside/laguna-xs.2:free"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.GOOGLE, "gemini-2.5-flash"),
    ],
    "backend_coding": [
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.GROQ, "openai/gpt-oss-120b"),
    ],
    "debugging": [
        (Provider.GROQ, "llama-3.1-8b-instant"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        (Provider.GOOGLE, "gemini-3.5-flash"),
    ],
    "validation": [
        (Provider.GOOGLE, "gemini-2.5-flash"),
        (Provider.GROQ, "llama-3.3-70b-versatile"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        (Provider.GOOGLE, "gemini-3.5-flash"),
    ],
    "security_review": [
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        (Provider.OPENROUTER, "owl-alpha"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
    ],
    "docs_presentation": [
        (Provider.GOOGLE, "gemini-2.5-flash"),
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.GROQ, "openai/gpt-oss-120b"),
        (Provider.GROQ, "llama-3.3-70b-versatile"),
    ],
    "memory": [
        (Provider.GROQ, "llama-3.1-8b-instant"),
        (Provider.GOOGLE, "gemini-embedding-2"),
        (Provider.CLOUDFLARE, "BGE-embedding-models"),
    ],
    "vision_ui": [
        (Provider.GOOGLE, "gemini-3.5-flash"),
        (Provider.GOOGLE, "gemini-2.5-flash"),
        (Provider.CLOUDFLARE, "kimi-k2.6"),
    ],
}


def get_task_chain(task_type: str) -> List[Tuple[Provider, str]]:
    """Get the exact model chain for a task type."""
    return TASK_CHAINS.get(task_type, TASK_CHAINS["quick_routing"])


# ============================================================================
# CODE REPAIR ROLES - Optimized for code repair tasks
# ============================================================================

CODE_REPAIR_ROLES = {
    "issue_understanding": TaskRole.DEBUGGER,
    "file_locating": TaskRole.FILE_INSPECTOR,
    "patch_generation": TaskRole.BACKEND_CODER,
    "patch_validation": TaskRole.VALIDATOR,
    "test_execution": TaskRole.TESTING_AGENT,
    "error_fix": TaskRole.SELF_HEALING_AGENT,
}


def get_code_repair_model_chain() -> List[Tuple[Provider, str]]:
    """
    Get optimized model chain for code repair tasks.
    """
    return [
        # Step 1: Understand the issue
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        # Step 2: Locate relevant files
        (Provider.OPENROUTER, "qwen/qwen3-coder:free"),
        # Step 3: Generate patch
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
        # Step 4: Validate
        (Provider.GOOGLE, "gemini-2.5-flash"),
        # Step 5: Final check
        (Provider.GOOGLE, "gemini-3.5-flash"),
    ]

def run_code_repair_model_chain() -> List[Tuple[Provider, str]]:
    """
    Alias for get_code_repair_model_chain - for backwards compatibility.
    """
    return get_code_repair_model_chain()

# Alias for backwards compatibility

# ============================================================================
# SUMMARY STATS
# ============================================================================

def get_stats() -> Dict[str, Any]:
    """Get summary statistics about the model registry."""
    total_models = sum(len(models) for models in PROVIDER_MODELS.values())
    free_models = sum(
        1 for models in PROVIDER_MODELS.values()
        for m in models if is_free_model(m)
    )
    
    return {
        "total_roles": len(TaskRole),
        "total_models": total_models,
        "free_models": free_models,
        "paid_models": total_models - free_models,
        "providers": {
            p.value: len(models) for p, models in PROVIDER_MODELS.items()
        },
        "best_coding_model": "qwen/qwen3-coder:free",
        "best_reasoning_model": "nvidia/nemotron-3-super-120b-a12b:free",
        "best_context_model": "nvidia/nemotron-3-super-120b-a12b:free",  # 1M context
    }


# ============================================================================
# CONVENIENCE EXPORTS
# ============================================================================

__all__ = [
    "TaskRole",
    "Provider",
    "PROVIDER_MODELS",
    "ROLE_MODEL_ROUTING",
    "classify_task",
    "get_model_for_role",
    "get_model_chain",
    "get_models_for_provider",
    "is_free_model",
    "get_best_free_model",
    "get_model_info",
    "get_task_chain",
    "get_code_repair_model_chain",
    "run_code_repair_model_chain",
    "get_stats",
]
