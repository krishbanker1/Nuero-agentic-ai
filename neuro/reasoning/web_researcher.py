"""
Web Research Module - Autonomous research before building applications
Uses Tavily API and browser tools to research unknown topics
"""

import html as html_utils
import json
import re
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Try to import Tavily for web search
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# Browser tools for research
try:
    from browser_automation import BrowserAutomation
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False


@dataclass
class ResearchResult:
    """Result of web research."""
    topic: str
    summary: str = ""
    key_features: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    raw_content: str = ""
    code_patterns: List[str] = field(default_factory=list)  # NEW: actual code snippets
    file_structure: Dict[str, str] = field(default_factory=dict)  # NEW: file -> language mapping
    cloned_repos: List[str] = field(default_factory=list)  # NEW: cloned repo URLs
    success: bool = False
    error: str = ""


class WebResearcher:
    """
    Autonomous web research module.
    Researches unknown topics before building applications.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_tavily_key()
        self.tavily_client = None
        if TAVILY_AVAILABLE and self.api_key:
            try:
                self.tavily_client = TavilyClient(api_key=self.api_key)
            except Exception:
                pass
        
        self.browser = None
        if BROWSER_AVAILABLE:
            try:
                self.browser = BrowserAutomation()
            except Exception:
                pass
    
    def _get_tavily_key(self) -> Optional[str]:
        """Get Tavily API key from environment."""
        return os.environ.get("TAVILY_API_KEY")
    
    def research(self, topic: str, depth: str = "basic") -> ResearchResult:
        """
        Research a topic thoroughly.
        
        Args:
            topic: The topic to research
            depth: Research depth - "basic", "advanced", or "comprehensive"
        
        Returns:
            ResearchResult with findings
        """
        result = ResearchResult(topic=topic)
        
        # Step 0: Direct URL crawl when the goal includes docs/examples URLs.
        direct_info = self._crawl_direct_urls(topic)
        if direct_info:
            result.summary = direct_info.get("summary", "")
            result.key_features = direct_info.get("features", [])
            result.tech_stack = direct_info.get("tech_stack", [])
            result.references = direct_info.get("references", [])
            result.raw_content = direct_info.get("raw_content", "")
            result.success = True

        # Step 1: Try GitHub search FIRST (free, no API key needed)
        if not result.success:
            print(f"🔍 Searching GitHub for: {topic}")
        github_info = None if result.success else self._search_github(topic)
        if github_info:
            result.key_features = github_info.get("features", [])
            result.tech_stack = github_info.get("tech_stack", [])
            result.references = [github_info.get("url", "")]
            result.summary = github_info.get("description", "")
            result.success = True
            print(f"✅ GitHub research complete: {len(result.key_features)} features")
            
            # Always enrich with topic-based features for comprehensive coverage
            topic_features = self._extract_features_from_topic(topic)
            if topic_features:
                result.key_features = list(set(result.key_features + topic_features))[:20]
                print(f"✅ Enriched with {len(topic_features)} domain-specific features")
        
        # Step 2: Try Tavily search only if free/no-auth sources did not answer.
        if self.tavily_client and not result.success:
            try:
                print(f"🔍 Searching Tavily for: {topic}")
                search_result = self.tavily_client.search(
                    query=topic,
                    search_depth=depth,
                    max_results=5
                )
                result.raw_content = json.dumps(search_result, indent=2)
                result.references = [r.get("url", "") for r in search_result.get("results", [])]
                if not result.summary:
                    result.summary = self._extract_summary(search_result)
                result.success = True
            except Exception as e:
                print(f"⚠️ Tavily search failed: {e}")
        
        # Step 3: Try DuckDuckGo HTML search (free, no auth/card)
        if not result.success:
            print(f"🔍 Searching DuckDuckGo for: {topic}")
            ddg_info = self._search_duckduckgo(topic)
            if ddg_info:
                result.summary = ddg_info.get("summary", "")
                result.key_features = ddg_info.get("features", [])
                result.tech_stack = ddg_info.get("tech_stack", [])
                result.references = ddg_info.get("references", [])
                result.raw_content = ddg_info.get("raw_content", "")
                result.success = True

        # Step 4: Try browser-based research as last resort
        if not result.success:
            print(f"🔍 Using browser for: {topic}")
            browser_info = self._research_with_browser(topic)
            if browser_info:
                result.summary = browser_info.get("summary", "")
                result.key_features = browser_info.get("features", [])
                result.tech_stack = browser_info.get("tech_stack", [])
                result.success = True
        
        # If all failed, generate basic research from topic name
        if not result.success:
            result.summary = f"Application: {topic}"
            result.key_features = self._extract_features_from_topic(topic)
            result.tech_stack = ["Python", "Flask", "SQLAlchemy"]
            result.success = True
            print(f"⚠️ Using basic research for: {topic}")
        
        return result
    
    def _extract_summary(self, search_result: Dict) -> str:
        """Extract summary from Tavily results."""
        results = search_result.get("results", [])
        if not results:
            return ""
        
        summary_parts = []
        for r in results[:3]:
            title = r.get("title", "")
            snippet = r.get("content", "")
            if snippet:
                summary_parts.append(f"- {title}: {snippet[:200]}")
        
        return "\n".join(summary_parts)
    
    def _search_github(self, topic: str) -> Optional[Dict[str, Any]]:
        """Search GitHub for relevant repositories without shelling out."""
        try:
            # Extract key terms from topic for better search
            search_terms = self._extract_search_terms(topic)
            
            # Search for multiple related terms
            all_features = []
            all_tech = []
            descriptions = []
            repo_urls = []
            
            for term in search_terms[:5]:  # Limit API calls
                query = urllib.parse.urlencode({
                    "q": term,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": "3",
                })
                request = urllib.request.Request(
                    f"https://api.github.com/search/repositories?{query}",
                    headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "NeuroResearcher/1.0"},
                )
                with urllib.request.urlopen(request, timeout=15) as response:
                    data = json.loads(response.read().decode("utf-8", errors="ignore"))
                repos = data.get("items", [])
                
                for repo in repos:
                    desc = repo.get("description", "")
                    if desc and desc not in descriptions:
                        descriptions.append(desc)
                        repo_urls.append(repo.get("html_url", ""))
                    all_features.extend(self._extract_features_from_description(desc))
                    all_tech.extend(self._extract_tech_stack(repo))
            
            if descriptions or all_features:
                return {
                    "name": topic,
                    "description": " | ".join([d for d in descriptions if d][:3]),
                    "features": list(set(all_features))[:15],
                    "tech_stack": list(set(all_tech))[:10],
                    "url": repo_urls[0] if repo_urls else ""
                }
        except Exception as e:
            print(f"GitHub search error: {e}")
        return None

    def _crawl_direct_urls(self, text: str) -> Optional[Dict[str, Any]]:
        """Fetch direct URLs from the prompt as a free research source."""
        urls = self._extract_urls(text)[:3]
        if not urls:
            return None

        pages = []
        for url in urls:
            try:
                page = self._fetch_url_text(url)
            except (urllib.error.URLError, TimeoutError, OSError, ValueError):
                continue
            if page:
                pages.append({"url": url, "content": page[:8000]})

        if not pages:
            return None

        combined = "\n".join(page["content"] for page in pages)
        return {
            "summary": combined[:1200],
            "features": self._extract_features_from_description(combined),
            "tech_stack": self._extract_tech_terms(combined),
            "references": [page["url"] for page in pages],
            "raw_content": json.dumps(pages, indent=2),
        }

    @staticmethod
    def _extract_urls(text: str) -> List[str]:
        """Extract HTTP(S) URLs while trimming punctuation from prose."""
        urls = re.findall(r"https?://[^\s)>'\"]+", text)
        cleaned = []
        for url in urls:
            normalized = url.rstrip(".,;:]")
            if normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned

    def _fetch_url_text(self, url: str) -> str:
        """Fetch and strip a single URL with no API key/card requirement."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Only HTTP(S) URLs can be crawled")
        request = urllib.request.Request(url, headers={"User-Agent": "NeuroResearcher/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "") if hasattr(response, "headers") else ""
            raw = response.read().decode("utf-8", errors="ignore")
        if "html" in content_type.lower() or "<html" in raw[:500].lower():
            raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.IGNORECASE)
            raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.IGNORECASE)
            return self._strip_html(raw)
        return re.sub(r"\s+", " ", raw).strip()

    def _search_duckduckgo(self, topic: str) -> Optional[Dict[str, Any]]:
        """Search DuckDuckGo HTML results without an API key or paid service."""
        try:
            query = urllib.parse.urlencode({"q": topic})
            request = urllib.request.Request(
                f"https://duckduckgo.com/html/?{query}",
                headers={"User-Agent": "Mozilla/5.0 NeuroResearcher/1.0"},
            )
            with urllib.request.urlopen(request, timeout=15) as response:
                page = response.read().decode("utf-8", errors="ignore")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if self.api_key:
                print(f"DuckDuckGo search error: {exc}")
            return None

        matches = list(re.finditer(
            r'<a[^>]+class="result__a"[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>',
            page,
            flags=re.IGNORECASE | re.DOTALL,
        ))
        results = []
        for index, match in enumerate(matches[:5]):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else start + 1200
            snippet_match = re.search(
                r'<a[^>]+class="result__snippet"[^>]*>(?P<snippet>.*?)</a>',
                page[start:end],
                flags=re.IGNORECASE | re.DOTALL,
            )
            title = self._strip_html(match.group("title"))
            url = self._normalize_duckduckgo_url(html_utils.unescape(match.group("url")))
            snippet = self._strip_html(snippet_match.group("snippet")) if snippet_match else ""
            if title or snippet:
                results.append({"title": title, "url": url, "snippet": snippet})

        if not results:
            return None

        summary = "\n".join(
            f"- {item['title']}: {item['snippet']}".strip()
            for item in results[:3]
            if item.get("title") or item.get("snippet")
        )
        combined_text = " ".join(
            f"{item.get('title', '')} {item.get('snippet', '')}"
            for item in results
        )
        return {
            "summary": summary,
            "features": self._extract_features_from_description(combined_text),
            "tech_stack": self._extract_tech_terms(combined_text),
            "references": [item["url"] for item in results if item.get("url")],
            "raw_content": json.dumps(results, indent=2),
        }

    @staticmethod
    def _strip_html(text: str) -> str:
        """Convert a small HTML fragment into readable text."""
        no_tags = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", html_utils.unescape(no_tags)).strip()

    @staticmethod
    def _normalize_duckduckgo_url(url: str) -> str:
        """Unwrap DuckDuckGo redirect URLs when possible."""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params and params["uddg"]:
            return params["uddg"][0]
        return url

    @staticmethod
    def _extract_tech_terms(text: str) -> List[str]:
        """Extract common framework/runtime names from free-search snippets."""
        terms = [
            "Python", "FastAPI", "Flask", "Django", "React", "Next.js",
            "Vue", "Angular", "Node.js", "Express", "PostgreSQL", "MySQL",
            "SQLite", "Redis", "Docker", "Tailwind", "TypeScript", "JavaScript",
            "GraphQL", "REST", "WebSocket", "Kubernetes",
        ]
        text_lower = text.lower()
        found = []
        for term in terms:
            if term.lower() in text_lower and term not in found:
                found.append(term)
        return found[:10]

    def _extract_search_terms(self, topic: str) -> List[str]:
        """Extract multiple search terms from topic for comprehensive research."""
        # Base terms from the topic
        terms = [topic.lower()]
        
        # Extract meaningful words
        words = topic.lower().replace("-", " ").replace("_", " ").split()
        
        # Common domain patterns to expand search
        domain_patterns = {
            "tuner": ["piano tuning", "guitar tuner", "instrument tuner", "FFT tuning", "frequency analysis"],
            "piano": ["piano tuning", "music production", "audio analysis", "instrument tuning"],
            "music": ["audio processing", "music production", "sound analysis", "audio visualization"],
            "chat": ["real-time messaging", "websocket chat", "messaging app", "chat application"],
            "crm": ["customer management", "sales crm", "business crm", "enterprise crm"],
            "cms": ["content management", "blog cms", "website cms", "enterprise cms"],
            "ecommerce": ["online store", "shopping cart", "payment integration", "e-commerce platform"],
            "social": ["social network", "user profiles", "social media", "community platform"],
            "analytics": ["data visualization", "dashboard analytics", "business intelligence", "metrics"],
            "automation": ["workflow automation", "process automation", "business rules", "triggers"],
        }
        
        for word in words:
            if word in domain_patterns:
                terms.extend(domain_patterns[word])
        
        # Add generic tech search if we haven't found specific matches
        if len(terms) < 3:
            terms.extend(["open source", "github", "enterprise application"])
        
        return list(set(terms))[:10]
    
    def _extract_features_from_description(self, description: str) -> List[str]:
        """Extract key features from a description."""
        if not description:
            return []
        
        features = []
        desc_lower = description.lower()
        
        # Look for technical feature patterns
        patterns = [
            # Audio/signal processing
            r'(fft|fast fourier|frequency analysis|pitch detection|autocorrelation)',
            r'(spectrum analyzer|strobe|tuning fork|piano tuning|instrument tuner)',
            r'(audio processing|sound analysis|dsp|signal processing)',
            
            # Enterprise features
            r'(authentication|authorization|rbac|permissions|access control)',
            r'(multi-tenant|saas|cloud deployment|scalable)',
            r'(rest api|graphql|websockets|real-time|grpc)',
            r'(database|orm|sql|no-sql|caching|redis|memcached)',
            r'(docker|kubernetes|deployment|ci/cd|devops)',
            r'(admin dashboard|reporting|analytics|business intelligence)',
            r'(email|notifications|webhooks|integrations)',
            r'(payments|stripe|billing|subscriptions|invoicing)',
            r'(audit logging|audit trail|compliance|soc2|gdpr)',
            r'(testing|unit tests|integration tests|test coverage)',
            r'(security|encryption|ssl|tls|https|2fa|mfa)',
            
            # UI/UX
            r'(responsive|mobile-first|pwa|progressive web app)',
            r'(dashboard|data visualization|charts|graphs)',
            r'(dark mode|theming|customization)',
            r'(drag.drop|drag and drop|sortable|reorderable)',
            r'(modal|toast|notification|alerts)',
            r'(search|filter|pagination|sorting)',
            r'(export|import|csv|excel|pdf)',
            
            # General features
            r'(crud|create.read.update.delete|api endpoints)',
            r'(crud|user management|role management|admin panel)',
            r'(crud|file upload|media management|image processing)',
            r'(crud|comments|reviews|ratings|feedback)',
            r'(crud|messaging|notifications|activity feed)',
            r'(crud|search|filter|analytics|reporting)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, desc_lower)
            features.extend(matches)
        
        return list(set(features))[:10]
    
    def _extract_features_from_topic(self, topic: str) -> List[str]:
        """Extract features from topic name for enterprise-level app."""
        words = topic.lower().replace("-", " ").replace("_", " ").split()
        
        features = []
        topic_lower = " ".join(words)
        
        # Audio/tuning specific features
        if any(w in topic_lower for w in ['tuner', 'piano', 'music', 'audio', 'sound']):
            features.extend([
                'microphone input capture',
                'FFT frequency analysis',
                'pitch detection algorithm',
                'real-time waveform display',
                'spectrum analyzer visualization',
                'strobe tuning mode',
                'needle meter display',
                'note identification (A0-C8)',
                'cents deviation display',
                'stretch tuning support',
                'equal temperament',
                'custom temperaments (Werckmeister, Kirnberger)',
                'audio recording and playback',
                'tuning history tracking',
                'export tuning data'
            ])
        
        # Generic enterprise features for any app
        generic_enterprise = [
            'user authentication (email/password, OAuth, 2FA)',
            'role-based access control (admin, user, guest)',
            'RESTful API with proper versioning',
            'database with migrations',
            'input validation and sanitization',
            'error handling and logging',
            'responsive mobile-first UI',
            'dark mode support',
            'export data (CSV, Excel, PDF)',
            'email notifications',
            'admin dashboard',
            'audit logging',
            'API documentation',
            'Docker deployment',
            'CI/CD pipeline',
            'unit and integration tests'
        ]
        
        if not features:
            features = generic_enterprise[:10]
        
        return features
    
    def _extract_tech_stack(self, repo: Dict) -> List[str]:
        """Extract tech stack from repository."""
        tech = []
        
        language = repo.get("language", "")
        if language:
            tech.append(language)
        
        topics = repo.get("topics", [])
        if topics:
            tech.extend(topics[:5])
        
        return tech
    
    def _research_with_browser(self, topic: str) -> Optional[Dict[str, Any]]:
        """Research using browser automation."""
        if not self.browser:
            return None
        
        try:
            # Navigate to GitHub search
            search_url = f"https://github.com/search?q={topic.replace(' ', '+')}&type=repositories"
            self.browser.navigate(search_url)
            
            # Get page content
            content = self.browser.get_content()
            
            if content:
                return {
                    "summary": content[:1000],
                    "features": self._extract_features_from_description(content),
                    "tech_stack": []
                }
        except Exception:
            pass
        
        return None
    
    def build_research_context(self, result: ResearchResult) -> str:
        """
        Build a context string from research results for the AI.
        """
        context = f"""
RESEARCH RESULTS FOR: {result.topic}
{'=' * 50}

SUMMARY:
{result.summary}

KEY FEATURES IDENTIFIED:
"""
        for i, feature in enumerate(result.key_features, 1):
            context += f"{i}. {feature}\n"
        
        if result.tech_stack:
            context += """
RECOMMENDED TECH STACK:
"""
            for tech in result.tech_stack:
                context += f"- {tech}\n"
        
        if result.references:
            context += """
REFERENCES:
"""
            for ref in result.references[:5]:
                context += f"- {ref}\n"
        
        context += """
IMPORTANT: Use this research to build an application that matches
the domain and features identified above. Do NOT build a generic app.
"""
        
        return context


def quick_research(topic: str) -> ResearchResult:
    """Quick research function."""
    return WebResearcher().research(topic)


# Standalone research function for use in thinking loop
def research_topic(topic: str) -> str:
    """
    Research a topic and return context for AI.
    Use this before building applications for unknown topics.
    """
    researcher = WebResearcher()
    result = researcher.research(topic)
    
    if result.success:
        return researcher.build_research_context(result)
    else:
        return f"""
RESEARCH NOTE: Could not research '{topic}' automatically.
Please provide more details about what you want to build.
"""
