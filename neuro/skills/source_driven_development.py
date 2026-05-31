"""Source-Driven Development - Ground decisions in official docs using REAL AI"""
from neuro.router.smart_router import SmartRouter

class SourceDrivenDevelopment:
    """Use official documentation for authoritative code."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def research(self, topic: str, framework: str = "") -> str:
        """Research using official sources."""
        
        prompt = f"""Research {topic} using official documentation:

Framework: {framework if framework else "general"}

Find and cite:
- Official docs/guides
- Best practices
- Correct API usage
- Common mistakes to avoid

Output research with source citations.
"""
        
        return self.router.chat(prompt, task_type="deep_research")
    
    def generate_with_sources(self, task: str, framework: str) -> str:
        """Generate code grounded in official docs."""
        prompt = f"""Generate {task} using official {framework} docs:

Follow:
- Official patterns
- Recommended approaches
- Best practices
- Correct types/APIs

Output code with comments citing sources.
"""
        return self.router.chat(prompt, task_type="source_driven_development")


def research_framework(topic: str, framework: str) -> str:
    """Quick framework research."""
    return SourceDrivenDevelopment().research(topic, framework)
