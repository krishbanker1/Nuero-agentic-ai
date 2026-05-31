from neuro.skills import SKILL_REGISTRY, invoke_skill, invoke_skill_class
from neuro.skills.rest_api_builder import RESTAPIBuilder
from neuro.skills.skill_orchestrator import SkillOrchestrator


class LegacyBuildSkill:
    def build(self, description: str):
        return {"description": description, "artifact": "built"}


class LegacyGenerateSkill:
    def generate(self, description: str):
        return f"generated: {description}"


class MultiMethodSkill:
    def suggest_workflow(self, team_size: int, project_type: str):
        return "should be skipped because it needs two required args"

    def write_commit_message(self, changes: str):
        return f"fix: {changes}"


def test_invoke_skill_class_adapts_legacy_build_method():
    result = invoke_skill_class("legacy_build", LegacyBuildSkill, "build a CRM")

    assert result["success"] is True
    assert result["skill"] == "legacy_build"
    assert result["method"] == "build"
    assert result["description"] == "build a CRM"
    assert result["artifact"] == "built"


def test_invoke_skill_class_wraps_string_results():
    result = invoke_skill_class("legacy_generate", LegacyGenerateSkill, "hero section")

    assert result["success"] is True
    assert result["method"] == "generate"
    assert result["result"] == "generated: hero section"


def test_invoke_skill_class_skips_unsuitable_methods():
    result = invoke_skill_class("multi_method", MultiMethodSkill, "parser recovery")

    assert result["success"] is True
    assert result["method"] == "write_commit_message"
    assert result["result"] == "fix: parser recovery"


def test_template_builder_is_registered_and_invokable(monkeypatch):
    def fake_chat(self, prompt, task_type="general", **kwargs):
        return f"fake {task_type}: {prompt[:18]}"

    monkeypatch.setattr("neuro.router.smart_router.SmartRouter.chat", fake_chat)

    assert SKILL_REGISTRY["rest_api_builder"] is RESTAPIBuilder
    result = invoke_skill("rest_api_builder", "Build a job board API")

    assert result["success"] is True
    assert result["method"] == "build"
    assert result["framework"] == "express"
    assert result["routes"].startswith("fake api_development")


def test_skill_orchestrator_invokes_non_invoke_registry_skill(monkeypatch):
    def fake_chat(self, prompt, task_type="general", **kwargs):
        return "generated api"

    monkeypatch.setattr("neuro.router.smart_router.SmartRouter.chat", fake_chat)

    orchestrator = SkillOrchestrator(verbose=False)
    orchestrator.active_skills = ["rest_api_builder"]
    enriched = orchestrator.enrich_context("Build a REST API", {})

    assert enriched is not None
    assert orchestrator.skill_results["rest_api_builder"]["success"] is True
    assert orchestrator.skill_results["rest_api_builder"]["method"] == "build"
