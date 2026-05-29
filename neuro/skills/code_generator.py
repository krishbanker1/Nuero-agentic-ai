"""Code Generator - Complete code generation for all languages"""
from typing import Dict, Any, Optional
from neuro.router.smart_router import SmartRouter

class CodeGenerator:
    """Advanced code generation using real AI models."""
    MODEL = "groq/llama-3.3-70b-versatile"  # Fast and capable
    
    def __init__(self):
        self.router = SmartRouter()
    
    def generate(self, description: str, language: str = "python", framework: str = None) -> str:
        """Generate complete code from description using REAL AI."""
        
        prompt = f"""You are an expert {language} developer. Generate COMPLETE, WORKING code for:

{description}

Requirements:
- Use {" " + framework + " framework" if framework else "best practices for " + language}
- Include error handling
- Add docstrings/comments
- Make it production-ready

Output ONLY the code, nothing else. No markdown, no explanations.
"""
        
        result = self.router.chat(prompt, task_type="code_generation")
        return result
    
    def generate_full_stack(self, spec: Dict) -> Dict[str, str]:
        """Generate complete full-stack application."""
        components = {}
        
        if spec.get("frontend"):
            prompt = f"""Generate complete React frontend for: {spec.get('description', 'Application')}
Include:
- App.jsx with routing
- Dashboard component
- Forms with validation
- API integration
Output ONLY code, no markdown."""
            components["frontend"] = self.router.chat(prompt, task_type="frontend_react")
        
        if spec.get("backend"):
            prompt = f"""Generate complete Node.js/Express backend with:
- REST endpoints
- JWT authentication
- Database models
- Error handling
Output ONLY code, no markdown."""
            components["backend"] = self.router.chat(prompt, task_type="backend_api")
        
        if spec.get("database"):
            prompt = f"""Generate PostgreSQL schema with:
- Users table with roles
- Relationships
- Indexes
- Triggers for timestamps
Output ONLY SQL code."""
            components["database"] = self.router.chat(prompt, task_type="database_sql")
        
        return components


def quick_generate(description: str, language: str = "python") -> str:
    """Quick code generation using real AI."""
    gen = CodeGenerator()
    return gen.generate(description, language)
