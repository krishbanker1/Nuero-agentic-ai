"""Tests for staged production build pipeline planning."""

from neuro.reasoning.thinking_loop import LoopConfig, PassType, ThinkingLoop
from neuro.skills.production_build_pipeline import ProductionBuildPipeline
from neuro.skills.skill_orchestrator import SkillOrchestrator


class _DummyRouter:
    def complete(self, messages, **kwargs):
        return {"content": "{}"}


def test_pipeline_creates_staged_fullstack_plan():
    plan = ProductionBuildPipeline.create_plan("build enterprise CRM dashboard")

    assert plan.scaffold.stack == "fullstack_fastapi_static"
    assert [stage.name for stage in plan.stages] == [
        "spec_and_contract",
        "backend_and_data",
        "frontend_experience",
        "tests_and_deployment",
    ]
    assert any("app/main.py" in stage.files for stage in plan.stages)
    assert any("No paid" in gate for gate in plan.final_gates)


def test_pipeline_progress_reports_stage_repair_prompts():
    plan = ProductionBuildPipeline.create_plan("build REST API for orders")
    progress = ProductionBuildPipeline.validate_progress(
        [
            {"path": "SPEC.md", "content": "Orders API"},
            {"path": "README.md", "content": "Run locally"},
        ],
        plan,
    )

    assert progress["passed"] is False
    assert any(not stage["passed"] and stage["repair_prompt"] for stage in progress["stages"])


def test_orchestrator_adds_pipeline_context_for_build_goals():
    orchestrator = SkillOrchestrator(verbose=False)
    skills = orchestrator.detect_skills("build a SaaS admin portal", {"working_dir": "."})
    context = orchestrator.enrich_context("build a SaaS admin portal", {"working_dir": "."})

    assert "production_pipeline" in skills
    assert context["production_build_plan"]["stages"]
    assert "Stage 1" in context["production_pipeline_prompt"]


def test_thinking_loop_includes_pipeline_prompt():
    loop = ThinkingLoop(_DummyRouter(), LoopConfig(max_passes=1))
    prompt = loop._create_pass_prompt(
        4,
        PassType.IMPLEMENTATION,
        "build enterprise CRM",
        {"production_pipeline_prompt": "Stage 1: spec_and_contract"},
    )

    assert "Stage-by-stage production build pipeline" in prompt
    assert "spec_and_contract" in prompt
