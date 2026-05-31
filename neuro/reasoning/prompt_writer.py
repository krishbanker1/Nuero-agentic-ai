"""
Prompt Writer - Enterprise-grade prompt generation using FREE AI models
Uses ONLY Gemini and Groq models (best for prompt writing)
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PromptResult:
    """Result of prompt writing."""
    original_goal: str
    enhanced_prompt: str
    plan: str
    features: list
    tech_stack: list
    success: bool
    error: str = ""


class PromptWriter:
    """
    Enterprise Prompt Writer - Converts research into perfect prompts.
    
    Uses ONLY Gemini and Groq free models - best for prompt writing.
    """
    
    def __init__(self, router):
        self.router = router
        
        # Gemini models (best for complex reasoning and structured output)
        gemini_models = [
            "gemini-3.5-flash",        # Latest Gemini 3
            "gemini-2.5-flash",        # Gemini 2.5
            "gemini-2.5-flash",        # Gemini 2.0
            "gemini-flash-latest",    # Alias for latest
        ]
        
        # Groq models (fast, free tier)
        groq_models = [
            "llama-3.3-70b-versatile", # Groq's best model
            "llama-3.1-8b-instant",    # Groq's fast model
        ]
        
        # Combined priority list
        self.prompt_models = gemini_models + groq_models
    
    def write_enterprise_prompt(
        self,
        goal: str,
        research_context: str,
        domain_features: list
    ) -> PromptResult:
        """
        Convert goal + research into enterprise-grade implementation prompt.
        
        Args:
            goal: Original user goal
            research_context: Web research results
            domain_features: Identified features from research
            
        Returns:
            PromptResult with enhanced prompt and plan
        """
        
        system_prompt = """You are an ENTERPRISE SOFTWARE ARCHITECT and SENIOR PROMPT ENGINEER.

Your job is to create PERFECT implementation prompts that will result in 
PRODUCTION-READY, SELLABLE software.

You will receive:
1. A user goal (what they want to build)
2. Web research context (real-world examples and features)
3. Domain-specific features identified

You must output:
1. An ENHANCED PROMPT - The perfect prompt to give to a code generator
2. A DETAILED PLAN - Step-by-step implementation strategy
3. SELECTED TECH STACK - Best technologies for this domain
4. KEY FEATURES - Must-have features prioritized

RULES:
- The enhanced prompt should be SPECIFIC, not generic
- Include real technical details (algorithms, libraries, patterns)
- Specify architecture patterns (MVC, microservices, etc.)
- Include security requirements
- Specify deployment strategy
- Make it impossible to build a generic app

OUTPUT FORMAT (JSON):
{
  "enhanced_prompt": "The perfect, detailed prompt for code generation...",
  "plan": "Step 1: ...\nStep 2: ...\nStep 3: ...",
  "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
  "features": ["feature1", "feature2"],
  "architecture": "monolith|microservices|serverless",
  "security": ["auth", "encryption", "rate limiting"]
}
"""
        
        user_prompt = f"""
GOAL: {goal}

RESEARCH CONTEXT:
{research_context}

DOMAIN FEATURES IDENTIFIED:
{json.dumps(domain_features, indent=2)}

Create the perfect implementation prompt and plan for this application.
Consider:
- What makes this domain special?
- What real-world patterns should be followed?
- What enterprise features are essential?
- What would make this SELLABLE to customers?
"""
        
        try:
            response = self.router.complete(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2048,
                preferred_models=self.prompt_models,
                task_type="reasoning"
            )
            
            # Parse the JSON response
            result = self._parse_response(response, goal)
            return result
            
        except Exception as e:
            return PromptResult(
                original_goal=goal,
                enhanced_prompt=self._fallback_prompt(goal, domain_features),
                plan=self._fallback_plan(goal),
                features=domain_features,
                tech_stack=["Python", "Flask", "SQLAlchemy"],
                success=False,
                error=str(e)
            )
    
    def _parse_response(self, response: str, goal: str) -> PromptResult:
        """Parse the model response into structured result."""
        
        # Try to extract JSON
        try:
            # Find JSON block
            import re
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Try to find any JSON object
                json_match = re.search(r'\{[\s\S]*"enhanced_prompt"[\s\S]*\}', response)
                if json_match:
                    data = json.loads(json_match.group(0))
                else:
                    raise ValueError("No JSON found")
            
            return PromptResult(
                original_goal=goal,
                enhanced_prompt=data.get("enhanced_prompt", self._fallback_prompt(goal, [])),
                plan=data.get("plan", ""),
                features=data.get("features", []),
                tech_stack=data.get("tech_stack", ["Python", "Flask"]),
                success=True
            )
        except Exception:
            # Return raw response as enhanced prompt
            return PromptResult(
                original_goal=goal,
                enhanced_prompt=response,
                plan="See enhanced prompt for details",
                features=[],
                tech_stack=["Python", "Flask"],
                success=True
            )
    
    def _fallback_prompt(self, goal: str, features: list) -> str:
        """Generate a basic prompt if the model fails."""
        features_str = "\n".join([f"- {f}" for f in features[:10]])
        return f"""Build an enterprise-level {goal}.

REQUIRED FEATURES:
{features_str}

TECHNICAL REQUIREMENTS:
- Production-ready code with error handling
- RESTful API with proper versioning
- Database with migrations
- Authentication and authorization
- Input validation and sanitization
- Comprehensive logging
- Docker deployment ready
- CI/CD pipeline configuration

Deliver COMPLETE, WORKING code that can be sold to customers.
Output JSON with all files properly structured.
"""
    
    def _fallback_plan(self, goal: str) -> str:
        """Generate a basic plan if the model fails."""
        return f"""Implementation Plan for: {goal}

Step 1: Setup Project Structure
Step 2: Create Database Models
Step 3: Implement API Endpoints
Step 4: Build Frontend UI
Step 5: Add Authentication
Step 6: Testing and Validation
Step 7: Docker Setup
Step 8: Documentation
"""
    
    def enhance_with_code_patterns(
        self,
        prompt: str,
        code_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enhance an existing prompt with code patterns and best practices.
        
        Args:
            prompt: The base prompt to enhance
            code_context: Optional existing code to improve
            
        Returns:
            Enhanced prompt string
        """
        
        system_prompt = """You are a SENIOR SOFTWARE ENGINEER specializing in code patterns.

Given a prompt and optional existing code, enhance it with:
1. Best practices for the specific domain
2. Security considerations
3. Performance optimizations
4. Scalability patterns
5. Error handling strategies

Return ONLY the enhanced prompt text - no explanations.
"""
        
        user_prompt = f"""BASE PROMPT:
{prompt}
"""
        
        if code_context:
            user_prompt += f"""
EXISTING CODE:
{json.dumps(code_context, indent=2)}
"""
        
        try:
            return self.router.complete(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1024,
                preferred_models=self.prompt_models,
                task_type="reasoning"
            )
        except Exception:
            return prompt


def write_enterprise_prompt(
    router,
    goal: str,
    research_context: str,
    domain_features: list
) -> PromptResult:
    """Convenience function for prompt writing."""
    writer = PromptWriter(router)
    return writer.write_enterprise_prompt(goal, research_context, domain_features)