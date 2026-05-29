"""Code Review & Quality - Multi-axis code review using REAL AI"""
from typing import Dict, Any, List, Optional
from neuro.router.smart_router import SmartRouter

class CodeReviewQuality:
    """Multi-axis code review - correctness, readability, architecture, security, performance."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def review(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Review code across 5 axes using REAL AI."""
        
        prompt = f"""As an expert code reviewer, conduct a multi-axis code review for this {language} code:

```{language}
{code}
```

Review across 5 dimensions:
1. CORRECTNESS - Does it work? Edge cases, error handling, tests?
2. READABILITY - Clear names, logical structure, no clever tricks?
3. ARCHITECTURE - Follows patterns, clean boundaries, no duplication?
4. SECURITY - Input validation, no secrets, parameterized queries?
5. PERFORMANCE - N+1 queries, async where needed, efficient algorithms?

For each issue found:
- Severity: CRITICAL/HIGH/MEDIUM/LOW
- Dimension: which of the 5 axes
- Line/section: where the issue is
- Fix: specific recommendation

Output as structured review.
"""
        
        result = self.router.chat(prompt, task_type="code_review")
        
        return {
            "review": result,
            "code": code,
            "language": language,
            "dimensions": ["correctness", "readability", "architecture", "security", "performance"]
        }
    
    def quick_review(self, code: str) -> str:
        """Quick review with main issues."""
        prompt = f"""Review this code briefly. List top 3 critical issues and fixes:

{code}

Format: Issue | Fix | Severity
"""
        return self.router.chat(prompt, task_type="code_review")


def review_code(code: str, language: str = "python") -> Dict[str, Any]:
    """Quick code review."""
    return CodeReviewQuality().review(code, language)
