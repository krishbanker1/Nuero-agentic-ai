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
