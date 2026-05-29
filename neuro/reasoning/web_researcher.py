"""
Web Research Module - Autonomous research before building applications
Uses Tavily API and browser tools to research unknown topics
"""

import json
import re
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
        import os
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
        
        # Step 1: Try GitHub search FIRST (free, no API key needed)
        print(f"🔍 Searching GitHub for: {topic}")
        github_info = self._search_github(topic)
        if github_info:
            result.key_features = github_info.get("features", [])
            result.tech_stack = github_info.get("tech_stack", [])
            result.references = [github_info.get("url", "")]
            result.summary = github_info.get("description", "")
            result.success = True
            print(f"✅ GitHub research complete: {len(result.key_features)} features")
        
        # Step 2: Try Tavily search if available
        if self.tavily_client:
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
        
        # Step 3: Try browser-based research as last resort
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
        """Search GitHub for relevant repositories."""
        try:
            import subprocess
            import urllib.parse
            
            # Search GitHub API with proper encoding
            encoded_topic = urllib.parse.quote(topic)
            query = f"q={encoded_topic}&sort=stars&order=desc&per_page=5"
            cmd = f'curl -s -H "Accept: application/vnd.github.v3+json" "https://api.github.com/search/repositories?{query}"'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                repos = data.get("items", [])
                
                if repos:
                    # Aggregate features from top repos
                    all_features = []
                    all_tech = []
                    descriptions = []
                    
                    for repo in repos[:3]:
                        desc = repo.get("description", "")
                        if desc:
                            descriptions.append(desc)
                        all_features.extend(self._extract_features_from_description(desc))
                        all_tech.extend(self._extract_tech_stack(repo))
                    
                    return {
                        "name": repos[0].get("name", ""),
                        "description": " | ".join([d for d in descriptions if d][:2]),
                        "features": list(set(all_features))[:10],
                        "tech_stack": list(set(all_tech))[:10],
                        "url": repos[0].get("html_url", "")
                    }
        except Exception as e:
            print(f"GitHub search error: {e}")
        return None
    
    def _extract_features_from_description(self, description: str) -> List[str]:
        """Extract key features from a description."""
        if not description:
            return []
        
        # Look for common feature patterns
        features = []
        patterns = [
            r'(\w+\s+analysis)',
            r'(\w+\s+tracking)',
            r'(\w+\s+management)',
            r'(\w+\s+generation)',
            r'(\w+\s+automation)',
            r'(\w+\s+processing)',
            r'(\w+\s+tuning)',
            r'(\w+\s+spectrum)',
            r'(\w+\s+piano)',
            r'(\w+\s+frequency)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            features.extend(matches)
        
        return list(set(features))[:5]
    
    def _extract_features_from_topic(self, topic: str) -> List[str]:
        """Extract features from topic name."""
        words = topic.lower().replace("-", " ").replace("_", " ").split()
        
        # Common feature keywords
        feature_keywords = [
            "analysis", "tracking", "management", "generation", "automation",
            "processing", "tuning", "spectrum", "frequency", "audio",
            "visualization", "dashboard", "crm", "cms", "api", "database"
        ]
        
        features = []
        for word in words:
            if word in feature_keywords:
                features.append(word)
        
        if not features:
            features = ["user management", "data storage", "api endpoints"]
        
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
            context += f"""
RECOMMENDED TECH STACK:
"""
            for tech in result.tech_stack:
                context += f"- {tech}\n"
        
        if result.references:
            context += f"""
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
