"""Tests for free-first deterministic production scaffolding."""

from pathlib import Path

from neuro.skills.production_scaffolder import ProductionScaffolder
from neuro.skills.skill_orchestrator import SkillOrchestrator
from neuro.reasoning.thinking_loop import LoopConfig, PassType, ThinkingLoop


class _DummyRouter:
    def complete(self, messages, **kwargs):
        return {"content": "{}"}


def test_fullstack_scaffold_contains_enterprise_files_and_free_gates():
    plan = ProductionScaffolder.create_plan("build enterprise CRM dashboard website")

    assert plan.stack == "fullstack_fastapi_static"
    assert "app/main.py" in plan.required_paths()
    assert "static/index.html" in plan.required_paths()
    assert "Dockerfile" in plan.required_paths()
    assert any("No paid APIs" in gate for gate in plan.quality_gates)


def test_scaffold_file_set_validation_reports_missing_and_empty_files():
    plan = ProductionScaffolder.create_plan("build REST API for inventory")
    result = ProductionScaffolder.validate_file_set(
        [
            {"path": "SPEC.md", "content": "Inventory API"},
            {"path": "README.md", "content": ""},
        ],
        plan,
    )

    assert result["passed"] is False
    assert "README.md" in result["empty_files"]
    assert "app/main.py" in result["missing_required_files"]


def test_scaffold_workspace_validation_checks_non_empty_files(tmp_path: Path):
    plan = ProductionScaffolder.create_plan("static landing page")
    for rel_path in plan.required_paths():
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("ok", encoding="utf-8")

    assert ProductionScaffolder.validate_workspace(tmp_path, plan)["passed"] is True


def test_skill_orchestrator_adds_scaffold_context_for_app_builds():
    orchestrator = SkillOrchestrator(verbose=False)
    skills = orchestrator.detect_skills("build an enterprise SaaS dashboard", {"working_dir": "."})
    context = orchestrator.enrich_context("build an enterprise SaaS dashboard", {"working_dir": "."})

    assert "production_scaffolder" in skills
    assert context["production_scaffold"]["stack"] == "fullstack_fastapi_static"
    assert "Required files" in context["production_scaffold_prompt"]


def test_thinking_loop_includes_scaffold_prompt_in_implementation_pass():
    loop = ThinkingLoop(_DummyRouter(), LoopConfig(max_passes=1))
    prompt = loop._create_pass_prompt(
        4,
        PassType.IMPLEMENTATION,
        "build an enterprise CRM",
        {"production_scaffold_prompt": "Required files:\n- app/main.py"},
    )

    assert "Deterministic production scaffold" in prompt
    assert "app/main.py" in prompt
