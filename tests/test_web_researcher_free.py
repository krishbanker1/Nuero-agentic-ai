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


def test_direct_url_crawl_is_free_and_skips_search(monkeypatch):
    html = """
    <html><head><style>.x{}</style><script>alert('x')</script></head>
    <body><h1>FastAPI React CRM</h1><p>Authentication, PostgreSQL database, Docker deployment, tests.</p></body></html>
    """
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["headers"] = dict(request.header_items())
        seen["timeout"] = timeout
        return _FakeResponse(html)

    def fail_github(self, topic):
        raise AssertionError("GitHub search should not run when direct URL crawl succeeds")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr(WebResearcher, "_search_github", fail_github)

    researcher = WebResearcher(api_key=None)
    researcher.tavily_client = None
    researcher.browser = None

    result = researcher.research("Use https://example.com/docs/crm to build the app")

    assert result.success is True
    assert seen["url"] == "https://example.com/docs/crm"
    assert seen["timeout"] == 15
    assert "Authorization" not in seen["headers"]
    assert result.references == ["https://example.com/docs/crm"]
    assert "FastAPI React CRM" in result.summary
    assert "FastAPI" in result.tech_stack
    assert "PostgreSQL" in result.tech_stack
    assert "authentication" in " ".join(result.key_features)


def test_github_search_uses_urllib_not_shell(monkeypatch):
    payload = {
        "items": [{
            "description": "FastAPI app with authentication, Redis cache, PostgreSQL database, Docker deployment, and tests.",
            "html_url": "https://github.com/example/crm",
            "language": "Python",
            "topics": ["fastapi", "react"],
        }]
    }
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, dict(request.header_items()), timeout))
        return _FakeResponse(json.dumps(payload))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    researcher = WebResearcher(api_key=None)

    result = researcher._search_github("crm")

    assert result is not None
    assert calls
    assert calls[0][0].startswith("https://api.github.com/search/repositories?")
    assert calls[0][2] == 15
    assert "application/vnd.github.v3+json" in calls[0][1]["Accept"]
    assert result["url"] == "https://github.com/example/crm"
    assert "Python" in result["tech_stack"]
    assert "authentication" in result["features"]
