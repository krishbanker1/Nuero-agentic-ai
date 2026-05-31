from neuro.errors import NeuroError, NeuroErrorCode, format_error
from neuro.models import APPROVED_MODELS, MODEL_REGISTRY
from neuro.router.smart_router import Provider, SmartRouter


def test_model_registry_names_are_unique_after_runtime_deduplication():
    names = [model.name for model in MODEL_REGISTRY]

    assert len(names) == len(set(names))
    assert len(APPROVED_MODELS) == len(set(APPROVED_MODELS))
    assert set(APPROVED_MODELS) == set(names)
    assert "groq/llama-3.3-70b-versatile" in names
    assert "openrouter/deepseek/deepseek-v4-flash:free" in names


def test_public_enterprise_modules_import_after_cleanup():
    from neuro.architecture import ArchitecturePlan
    from neuro.healing import ErrorClassifier
    from neuro.pipelines import EnterpriseAppPipeline, PipelineContext
    from neuro.product import ProductSpec, parse_goal
    from neuro.stacks import STACKS, get_stack

    assert ProductSpec is not None
    assert parse_goal("build a CRM").raw_goal
    assert ArchitecturePlan is not None
    assert ErrorClassifier is not None
    assert PipelineContext is not None
    assert EnterpriseAppPipeline is not None
    assert STACKS
    assert get_stack("fastapi_react") is not None


def test_smart_router_circuit_opens_and_recovers():
    router = SmartRouter()
    router.circuit_config.recovery_timeout = 1

    for _ in range(router.circuit_config.failure_threshold):
        router._record_failure(Provider.GROQ, "llama-3.3-70b-versatile", "boom")

    assert router._is_circuit_open(Provider.GROQ)

    router.stats.circuit_open_until[Provider.GROQ.value] = 0
    assert not router._is_circuit_open(Provider.GROQ)

    for _ in range(router.circuit_config.failure_threshold):
        router._record_failure(Provider.GROQ, "llama-3.3-70b-versatile", "boom")
    router._record_success(Provider.GROQ, "llama-3.3-70b-versatile")
    assert not router._is_circuit_open(Provider.GROQ)


def test_structured_errors_format_neuro_and_unknown_errors():
    error = NeuroError(NeuroErrorCode.PROVIDER_CIRCUIT_OPEN, "provider paused", {"provider": "groq"})

    assert format_error(error)["code"] == NeuroErrorCode.PROVIDER_CIRCUIT_OPEN.value
    assert format_error(RuntimeError("bad"))["code"] == NeuroErrorCode.SYSTEM_UNHANDLED.value
