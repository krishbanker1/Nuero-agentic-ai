import os

import pytest

from neuro.__main__ import _has_provider_key
from neuro.executor.agent_loop import AgentConfig, NeuroAgent
from neuro.router.fallback import FailureType, FallbackHandler
from neuro.skills.skill_orchestrator import SkillOrchestrator


def test_skill_auto_trigger_enriches_prompt_context():
    orchestrator = SkillOrchestrator(verbose=False)
    orchestrator.detect_skills("build a 3D React website with GSAP animations")
    context = orchestrator.enrich_context("build a 3D React website with GSAP animations", {})

    assert "skill_instructions" in context
    assert "react" in context["skill_instructions"].lower() or "three" in context["skill_instructions"].lower()
    assert context["auto_detected_skills"]


def test_agent_validate_written_files_reports_missing_and_empty(tmp_path):
    agent = NeuroAgent(AgentConfig(goal="test", working_dir=str(tmp_path), verbose=False))
    empty = tmp_path / "empty.py"
    non_empty = tmp_path / "ok.py"
    empty.write_text("")
    non_empty.write_text("print('ok')")

    result = agent._validate_written_files([str(empty), str(non_empty), str(tmp_path / "missing.py")])

    assert str(empty) in result
    assert str(tmp_path / "missing.py") in result
    assert str(non_empty) not in result


def test_fallback_uses_exponential_backoff_with_jitter(monkeypatch):
    waits = []
    monkeypatch.setattr("neuro.router.fallback.time.sleep", waits.append)
    monkeypatch.setattr("neuro.router.fallback.random.uniform", lambda start, end: 0)

    handler = FallbackHandler(router=None)
    rule = handler.rules[FailureType.TIMEOUT]

    def timeout_response():
        return {"error": "request timeout", "provider": "groq", "model": "test"}

    result = handler.execute_with_fallback(timeout_response, max_attempts=1)

    assert result["attempts"] == 1
    assert waits == [rule.wait_seconds * (2 ** 1)]


def test_provider_key_detection_accepts_singular_and_plural(monkeypatch):
    for key in list(os.environ):
        if key.endswith("_API_KEY") or key.endswith("_API_KEYS") or key == "HF_TOKEN":
            monkeypatch.delenv(key, raising=False)

    assert _has_provider_key() is False
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    assert _has_provider_key() is True


@pytest.mark.integration
def test_integration_real_hello_world(monkeypatch, tmp_path):
    if not os.getenv("GROQ_API_KEY") and not os.getenv("GROQ_API_KEYS"):
        pytest.skip("GROQ_API_KEY/GROQ_API_KEYS not set; skipping real LLM integration")

    # Keep the test bounded and avoid changing external state. A full live run is intentionally
    # gated by the environment key above and by dry_run=False in a temp workspace.
    agent = NeuroAgent(AgentConfig(
        goal="Create a Python file output.py that prints hello world",
        working_dir=str(tmp_path),
        max_steps=5,
        max_passes=1,
        dry_run=False,
        verbose=False,
    ))
    result = agent.run()

    output_file = tmp_path / "output.py"
    assert result.success or output_file.exists()
    if output_file.exists():
        assert output_file.stat().st_size > 0
        import subprocess
        import sys

        completed = subprocess.run([sys.executable, str(output_file)], capture_output=True, text=True, timeout=10)
        assert completed.returncode == 0
        assert "hello" in completed.stdout.lower()


def test_agent_safe_generated_write_enforces_workspace_and_non_empty(tmp_path):
    agent = NeuroAgent(AgentConfig(goal="test", working_dir=str(tmp_path), verbose=False))

    assert agent._write_generated_file("../escape.py", "print('bad')") is None
    assert agent._write_generated_file("empty.py", "   ") is None

    written = agent._write_generated_file("src/app.py", "print('ok')")

    assert written == str(tmp_path / "src" / "app.py")
    assert (tmp_path / "src" / "app.py").read_text(encoding="utf-8") == "print('ok')"


def test_agent_detects_workspace_validation_commands(tmp_path):
    agent = NeuroAgent(AgentConfig(goal="validate", working_dir=str(tmp_path), verbose=False))
    app = tmp_path / "app.py"
    app.write_text("print('ok')\n")
    commands = agent._detect_workspace_commands([str(app)])

    assert commands["install"] == []
    assert commands["validate"] == ["python -m py_compile app.py"]


def test_agent_runs_workspace_validation_with_shell_executor(tmp_path):
    agent = NeuroAgent(
        AgentConfig(
            goal="validate",
            working_dir=str(tmp_path),
            verbose=False,
            use_memory=False,
            use_skills=False,
            validation_commands=["python -c \"print('workspace ok')\""],
        )
    )
    app = tmp_path / "app.py"
    app.write_text("print('ok')\n")

    result = agent._run_workspace_validation([str(app)])

    assert result["enabled"] is True
    assert result["success"] is True
    assert any(item["command"] == "python -m py_compile app.py" for item in result["results"])
    assert any("workspace ok" in item["stdout"] for item in result["results"])


def test_shell_executor_invoke_reports_command_failure(tmp_path):
    from neuro.skills.shell_executor import ShellExecutor

    result = ShellExecutor.invoke("python -c \"raise SystemExit(3)\"", {"working_dir": str(tmp_path), "max_retries": 0})

    assert result["skill"] == "shell_executor"
    assert result["success"] is False
    assert result["exit_code"] == 3


def test_deep_research_skill_imports_without_optional_tavily():
    from neuro.skills import _lazy_get_skill

    assert _lazy_get_skill("deep_research") is not None


def test_dry_run_succeeds_when_plan_is_generated(monkeypatch, tmp_path):
    from types import SimpleNamespace

    from neuro.executor import agent_loop as agent_loop_module

    monkeypatch.setattr(agent_loop_module, "run_agent_swarm", lambda task: {"trace": []})

    class _ScenarioRouterStub:
        def detect_scenario(self, goal):
            return SimpleNamespace(value="coding"), 1.0

        def get_handler(self, scenario):
            return SimpleNamespace(special_instructions=[], approach="plan")

    class _ThinkingLoopStub:
        def __init__(self, router, config):
            pass

        def run(self, goal, context):
            return {
                "solution": "",
                "num_passes": 1,
                "convergence_score": 1.0,
                "passes": [{"response_preview": "Plan preview"}],
                "context": {"plan": "Plan: create hello.py and print hello world"},
            }

    monkeypatch.setattr(agent_loop_module, "ScenarioRouter", _ScenarioRouterStub)
    monkeypatch.setattr(agent_loop_module, "ThinkingLoop", _ThinkingLoopStub)

    agent = agent_loop_module.NeuroAgent(
        agent_loop_module.AgentConfig(
            goal="Create a hello world Python script and run it",
            working_dir=str(tmp_path),
            dry_run=True,
            verbose=False,
            use_memory=False,
            use_skills=False,
            use_decomposer=False,
            use_verification=False,
            use_security=False,
            use_orchestration=False,
            use_autonomous_loop=False,
        )
    )

    result = agent.run()

    assert result.success is True
    assert result.status == "completed"
    assert result.validation_passed is True
    assert result.steps >= 1
    assert "plan" in result.metadata
