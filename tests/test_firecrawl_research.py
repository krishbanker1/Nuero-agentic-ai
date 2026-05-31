import json
from neuro.reasoning.thinking_loop import LoopConfig, PassType, ThinkingLoop
from neuro.skills.firecrawl_research import FirecrawlConfig, FirecrawlResearchSkill
from neuro.skills.skill_orchestrator import SkillOrchestrator


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_firecrawl_is_optional_without_key_or_self_host(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("FIRECRAWL_API_URL", raising=False)

    result = FirecrawlResearchSkill.invoke("scrape https://example.com docs")

    assert result["enabled"] is False
    assert result["requires_paid_service"] is False
    assert result["status"] == "not_configured"
    assert "Do not require it for builds" in result["prompt_block"]


def test_firecrawl_self_hosted_endpoint_is_free_first(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_URL", "http://localhost:3002")
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)

    skill = FirecrawlResearchSkill()

    assert skill.config.enabled is True
    assert skill.config.is_self_hosted is True
    assert "Authorization" not in skill._headers()


def test_firecrawl_scrape_normalizes_markdown(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse({
            "success": True,
            "data": {
                "markdown": "# Docs\n\nInstall with pip.",
                "links": ["https://example.com/api"],
                "metadata": {"title": "Docs"},
            },
        })

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    skill = FirecrawlResearchSkill(FirecrawlConfig(api_url="http://localhost:3002", api_key="", timeout=7))

    result = skill.scrape("https://example.com/docs")

    assert result["success"] is True
    assert seen["url"] == "http://localhost:3002/v2/scrape"
    assert seen["timeout"] == 7
    assert seen["body"]["formats"] == ["markdown", "links"]
    assert result["markdown"].startswith("# Docs")
    assert result["links"] == ["https://example.com/api"]


def test_skill_orchestrator_wires_firecrawl_guidance(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("FIRECRAWL_API_URL", raising=False)

    orchestrator = SkillOrchestrator(verbose=False)
    skills = orchestrator.detect_skills("Research latest docs from https://example.com/docs", {})
    enriched = orchestrator.enrich_context("Research latest docs from https://example.com/docs", {})

    assert "firecrawl_research" in skills
    assert enriched["firecrawl_enabled"] is False
    assert enriched["firecrawl_status"] == "not_configured"
    assert "Firecrawl can improve live web/docs research" in enriched["firecrawl_prompt"]
    assert "firecrawl" in enriched["skill_hints"].lower()


def test_thinking_loop_includes_firecrawl_context_in_prompt():
    loop = ThinkingLoop(LoopConfig(max_passes=1))
    prompt = loop._create_pass_prompt(
        1,
        PassType.RESEARCH,
        "Build docs-aware app",
        {
            "firecrawl_prompt": "Use clean markdown only.",
            "firecrawl_context": "# API Docs\nImportant endpoint details.",
        },
    )

    assert "Optional Firecrawl research guidance" in prompt
    assert "Use clean markdown only." in prompt
    assert "# API Docs" in prompt
