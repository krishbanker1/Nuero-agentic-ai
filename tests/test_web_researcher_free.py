import json
from urllib.parse import quote

from neuro.reasoning.web_researcher import WebResearcher


class _FakeResponse:
    def __init__(self, body: str):
        self.body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


def test_duckduckgo_search_is_free_no_auth_fallback(monkeypatch):
    html = f'''
    <html><body>
      <a class="result__a" href="//duckduckgo.com/l/?uddg={quote('https://example.com/fastapi-crm')}">
        FastAPI CRM with React and PostgreSQL
      </a>
      <a class="result__snippet">Build a REST API with authentication, Docker, and admin dashboard.</a>
      <a class="result__a" href="https://example.com/nextjs-dashboard">Next.js Dashboard</a>
      <a class="result__snippet">React TypeScript dashboard with Redis cache and PostgreSQL.</a>
    </body></html>
    '''
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["headers"] = dict(request.header_items())
        seen["timeout"] = timeout
        return _FakeResponse(html)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    researcher = WebResearcher(api_key=None)

    result = researcher._search_duckduckgo("build crm app")

    assert result is not None
    assert "duckduckgo.com/html/" in seen["url"]
    assert seen["timeout"] == 15
    assert "Authorization" not in seen["headers"]
    assert result["references"][0] == "https://example.com/fastapi-crm"
    assert "FastAPI CRM" in result["summary"]
    assert "React" in result["tech_stack"]
    assert "PostgreSQL" in result["tech_stack"]
    assert "authentication" in " ".join(result["features"])


def test_research_uses_duckduckgo_before_generic_fallback(monkeypatch):
    payload = [{
        "title": "Flask Todo App",
        "url": "https://example.com/flask-todo",
        "snippet": "Flask app with authentication, database, Docker, and tests.",
    }]

    monkeypatch.setattr(WebResearcher, "_search_github", lambda self, topic: None)
    monkeypatch.setattr(WebResearcher, "_research_with_browser", lambda self, topic: None)
    monkeypatch.setattr(WebResearcher, "_search_duckduckgo", lambda self, topic: {
        "summary": "- Flask Todo App: Flask app with authentication, database, Docker, and tests.",
        "features": ["authentication", "database", "docker", "testing"],
        "tech_stack": ["Flask", "Docker"],
        "references": ["https://example.com/flask-todo"],
        "raw_content": json.dumps(payload),
    })

    researcher = WebResearcher(api_key=None)
    researcher.tavily_client = None
    researcher.browser = None

    result = researcher.research("build todo app")

    assert result.success is True
    assert result.summary.startswith("- Flask Todo App")
    assert result.tech_stack == ["Flask", "Docker"]
    assert result.references == ["https://example.com/flask-todo"]
    assert "authentication" in result.key_features
