"""Provider/model routing normalization tests."""

from neuro.models import MODEL_REGISTRY, MODEL_ROLES, TASK_CATEGORIES
from neuro.router import scenario_router
from neuro.router.smart_router import GOOGLE_MODELS, UNKNOWN_TASK_MODEL_CHAIN, Provider as SmartProvider, SmartRouter
from neuro.router.task_router import PROVIDER_MODELS, ROLE_MODEL_ROUTING, Provider as TaskProvider, TaskRole
from neuro.ultimate import model_registry as ultimate_registry

ALLOWED_GOOGLE = {
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-live-preview",
    "gemini-2.5-flash-native-audio-preview-12-2025",
    "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-flash-image",
    "gemini-embedding-2",
    "gemini-embedding-001",
}

BANNED_GEMINI_IDS = (
    "openrouter/google/gemini",
    "google/gemini",
    "gemini/gemini",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-flash-lite-preview-09-2025",
    "gemini-pro",
    "gemini--pro",
)


def _all_route_strings():
    values = []
    for category in TASK_CATEGORIES.values():
        values.append(category["primary"])
        values.extend(category.get("fallback", []))
    for role in MODEL_ROLES.values():
        values.append(role["primary"])
        values.extend(role.get("fallback", []))
    for handler in scenario_router.SCENARIO_HANDLERS.values():
        values.append(handler.model_primary)
        if handler.model_fallback:
            values.append(handler.model_fallback)
    for route in ROLE_MODEL_ROUTING.values():
        for provider, model in route["primary"] + route["fallback"]:
            values.append(model if provider == TaskProvider.GOOGLE else f"{provider.value}/{model}")
    for provider, config in SmartRouter.PROVIDERS.items():
        values.extend(model if provider == SmartProvider.GOOGLE else f"{provider.value}/{model}" for model in config.models)
    values.extend(ultimate_registry.FALLBACK_CHAINS.get("default", []))
    return values


def test_openrouter_registry_contains_zero_gemini_models():
    openrouter_models = [m.name for m in MODEL_REGISTRY if m.provider == "openrouter"]
    openrouter_models += PROVIDER_MODELS[TaskProvider.OPENROUTER]
    openrouter_models += SmartRouter.PROVIDERS[SmartProvider.OPENROUTER].models
    assert not [model for model in openrouter_models if "gemini" in model.lower()]


def test_google_registry_contains_only_native_allowed_ids():
    google_models = [m.name for m in MODEL_REGISTRY if m.provider == "google"]
    google_models += PROVIDER_MODELS[TaskProvider.GOOGLE]
    google_models += GOOGLE_MODELS
    assert set(google_models) <= ALLOWED_GOOGLE
    assert all("/" not in model for model in google_models)


def test_groq_owned_gpt_oss_is_not_registered_as_openrouter():
    openrouter_task_models = PROVIDER_MODELS[TaskProvider.OPENROUTER]
    assert "openai/gpt-oss-120b:free" not in openrouter_task_models
    assert "openai/gpt-oss-120b" in PROVIDER_MODELS[TaskProvider.GROQ]

    ultimate_gpt_oss = [model for model in ultimate_registry.MODEL_REGISTRY.values() if "gpt-oss" in model.id]
    assert ultimate_gpt_oss
    assert all(model.provider == ultimate_registry.ModelProvider.GROQ for model in ultimate_gpt_oss)


def test_no_banned_gemini_models_in_active_routing():
    route_strings = _all_route_strings()
    for value in route_strings:
        for banned in BANNED_GEMINI_IDS:
            assert not value.startswith(banned), value
        assert "gemini-2.0" not in value
        assert "gemini-1.5" not in value
        assert "gemini-pro" not in value


def test_code_roles_prefer_openrouter_qwen_or_deepseek_before_gemini():
    code_roles = [
        TaskRole.FRONTEND_CODER,
        TaskRole.BACKEND_CODER,
        TaskRole.FULL_STACK_CODER,
        TaskRole.DATABASE_CODER,
        TaskRole.AUTH_CODER,
        TaskRole.INTEGRATION_CODER,
        TaskRole.AGENTIC_CODER,
        TaskRole.SMALL_PATCH_CODER,
        TaskRole.REFACTOR_AGENT,
    ]
    for role in code_roles:
        primary = ROLE_MODEL_ROUTING[role]["primary"]
        assert primary[0][0] == TaskProvider.OPENROUTER
        assert any(name in primary[0][1] for name in ("qwen", "deepseek"))
        assert all(provider != TaskProvider.GOOGLE for provider, _ in primary[:3])


def test_planning_roles_may_use_gemini_35_flash():
    for role in (TaskRole.MAIN_PLANNER, TaskRole.LONG_HORIZON_PLANNER, TaskRole.FINAL_ORCHESTRATOR):
        assert (TaskProvider.GOOGLE, "gemini-3.5-flash") in ROLE_MODEL_ROUTING[role]["primary"]


def test_embedding_and_speech_roles_use_specialized_gemini_models():
    embedding_primary = ROLE_MODEL_ROUTING[TaskRole.EMBEDDING_AGENT]["primary"]
    assert embedding_primary[0] == (TaskProvider.GOOGLE, "gemini-embedding-2")
    assert all("embedding" in model or provider != TaskProvider.GOOGLE for provider, model in embedding_primary)

    speech_route = ROLE_MODEL_ROUTING[TaskRole.SPEECH_STT_AGENT]
    speech_models = [model for _, model in speech_route["primary"] + speech_route["fallback"]]
    assert "gemini-3.1-flash-tts-preview" in speech_models
    assert "gemini-2.5-flash-preview-tts" in speech_models


def test_unknown_task_chain_is_balanced_not_gemini_only():
    assert UNKNOWN_TASK_MODEL_CHAIN[0].startswith("groq/")
    assert any(model.startswith("gemini-") for model in UNKNOWN_TASK_MODEL_CHAIN)
    assert any(model.startswith("openrouter/") for model in UNKNOWN_TASK_MODEL_CHAIN)


def test_all_task_roles_have_primary_and_fallback_models():
    assert len(TaskRole) == len(ROLE_MODEL_ROUTING)
    for role in TaskRole:
        route = ROLE_MODEL_ROUTING[role]
        assert route["primary"], role
        assert route["fallback"], role
