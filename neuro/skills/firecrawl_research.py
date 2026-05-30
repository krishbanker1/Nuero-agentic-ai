"""Optional Firecrawl research skill.

This integration is deliberately free-first: it only calls Firecrawl when the
user has configured either a self-hosted/local API URL or an explicit API key.
It never changes Neuro's model/provider brain and never requires a paid service.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


DEFAULT_FIRECRAWL_API_URL = "https://api.firecrawl.dev"


@dataclass
class FirecrawlConfig:
    """Configuration for an optional Firecrawl API endpoint."""

    api_url: str = field(default_factory=lambda: os.getenv("FIRECRAWL_API_URL", DEFAULT_FIRECRAWL_API_URL))
    api_key: str = field(default_factory=lambda: os.getenv("FIRECRAWL_API_KEY", ""))
    timeout: int = 30

    @property
    def is_self_hosted(self) -> bool:
        """Return True when using a non-cloud Firecrawl endpoint."""
        return self.api_url.rstrip("/") != DEFAULT_FIRECRAWL_API_URL

    @property
    def enabled(self) -> bool:
        """Cloud requires a key; self-host/local can run without one."""
        return self.is_self_hosted or bool(self.api_key)


class FirecrawlResearchSkill:
    """Fetch clean markdown/links from optional Firecrawl for research context."""

    CAPABILITIES = [
        "scrape clean markdown from docs/pages",
        "crawl self-hosted/local Firecrawl without a paid key",
        "enrich research context without changing model routing",
    ]

    def __init__(self, config: FirecrawlConfig | None = None):
        self.config = config or FirecrawlConfig()

    @classmethod
    def invoke(cls, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """SkillOrchestrator-compatible entry point."""
        skill = cls()
        context = context or {}
        url = context.get("url") or cls._extract_url(task)

        result: dict[str, Any] = {
            "capabilities": cls.CAPABILITIES,
            "enabled": skill.config.enabled,
            "self_hosted": skill.config.is_self_hosted,
            "api_url": skill.config.api_url,
            "requires_paid_service": False,
        }

        if not skill.config.enabled:
            result.update({
                "status": "not_configured",
                "prompt_block": cls.prompt_block(configured=False),
            })
            return result

        if not url:
            result.update({
                "status": "ready",
                "prompt_block": cls.prompt_block(configured=True),
            })
            return result

        scrape = skill.scrape(url)
        result.update(scrape)
        if scrape.get("success"):
            result["firecrawl_context"] = scrape.get("markdown", "")[:6000]
        return result

    @staticmethod
    def _extract_url(text: str) -> str:
        match = re.search(r"https?://[^\s)>'\"]+", text)
        return match.group(0) if match else ""

    @staticmethod
    def prompt_block(configured: bool) -> str:
        """Prompt hint injected when Firecrawl is relevant."""
        if configured:
            return (
                "Optional Firecrawl web context is configured. Use it only for live docs/page research; "
                "prefer clean markdown, cite source URLs, and keep all generated code free/local-first."
            )
        return (
            "Firecrawl can improve live web/docs research if FIRECRAWL_API_URL points to a self-hosted "
            "instance, or FIRECRAWL_API_KEY is set for the hosted API. Do not require it for builds."
        )

    def scrape(self, url: str, formats: list[str] | None = None) -> dict[str, Any]:
        """Call Firecrawl v2 scrape and normalize markdown/metadata output."""
        if not self.config.enabled:
            return {
                "success": False,
                "status": "not_configured",
                "error": "Set FIRECRAWL_API_URL for self-hosted/local Firecrawl or FIRECRAWL_API_KEY for hosted Firecrawl.",
            }

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return {"success": False, "status": "invalid_url", "error": f"Invalid URL: {url}"}

        payload = {
            "url": url,
            "formats": formats or ["markdown", "links"],
            "onlyMainContent": True,
        }
        request = urllib.request.Request(
            f"{self.config.api_url.rstrip('/')}/v2/scrape",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return {"success": False, "status": "http_error", "error": f"Firecrawl HTTP {exc.code}"}
        except Exception as exc:
            return {"success": False, "status": "request_failed", "error": str(exc)}

        firecrawl_data = data.get("data", data)
        return {
            "success": bool(data.get("success", True)),
            "status": "ok",
            "url": url,
            "markdown": firecrawl_data.get("markdown", ""),
            "links": firecrawl_data.get("links", []),
            "metadata": firecrawl_data.get("metadata", {}),
            "raw": data,
        }

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers
