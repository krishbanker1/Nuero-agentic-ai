"""
Multi-Pass Thinking Loop - Core for 75-80% performance
Multiple reasoning passes to converge on solution
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Import web research module
try:
    from neuro.reasoning.web_researcher import research_topic, WebResearcher
    WEB_RESEARCH_AVAILABLE = True
except ImportError:
    WEB_RESEARCH_AVAILABLE = False


class PassType(Enum):
    """Types of reasoning passes."""
    RESEARCH = "research"  # NEW: Web research for unknown topics
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    DEBUGGING = "debugging"
    REFLECTION = "reflection"


@dataclass
class ThinkingPass:
    """A single thinking pass."""
    pass_type: PassType
    prompt: str
    response: str = ""
    duration_ms: float = 0
    success: bool = False
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopConfig:
    """Configuration for thinking loop."""
    max_passes: int = 6
    pass_timeout: int = 120  # seconds
    convergence_threshold: float = 0.8
    allow_stuck_detection: bool = True
    stuck_after_passes: int = 3


class ThinkingLoop:
    """
    Multi-pass thinking loop for robust problem solving.
    Key to achieving 75-80% by catching errors early.
    """
    
    def __init__(self, router, config: Optional[LoopConfig] = None):
        self.router = router
        self.config = config or LoopConfig()
        self.passes: List[ThinkingPass] = []
        self.convergence_score: float = 0.0
    
    def run(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        validate_fn: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Run multi-pass thinking loop.
        
        Args:
            goal: The task goal
            context: Optional context (code, files, errors)
            validate_fn: Optional validation function
            
        Returns:
            Dict with solution, passes, and metadata
        """
        self.passes = []
        context = context or {}
        best_solution = ""
        best_score = 0.0
        
        for pass_num in range(1, self.config.max_passes + 1):
            print(f"🔄 Pass {pass_num}/{self.config.max_passes}")
            
            # Determine pass type based on iteration
            pass_type = self._get_pass_type(pass_num, goal, context)
            
            # Create pass prompt
            prompt = self._create_pass_prompt(pass_num, pass_type, goal, context)
            
            # Execute pass
            start = time.time()
            response = self._execute_pass(prompt, context, pass_type)
            duration = (time.time() - start) * 1000
            
            # Score convergence
            score = self._score_convergence(response, best_solution)
            
            # Record pass
            thinking_pass = ThinkingPass(
                pass_type=pass_type,
                prompt=prompt,
                response=response,
                duration_ms=duration,
                success=True,
                metadata={"pass_num": pass_num, "score": score}
            )
            self.passes.append(thinking_pass)
            
            # Only update best_solution if it contains JSON (actual code)
            # Skip RESEARCH pass from best_solution consideration
            has_json = '"files"' in response or '"path"' in response
            if has_json and score > best_score:
                best_score = score
                best_solution = response
                print(f"   ✓ Pass {pass_num} complete (score: {score:.2f}) - JSON code found!")
            else:
                print(f"   ✓ Pass {pass_num} complete (score: {score:.2f})")
            
            # Check convergence
            if score >= self.config.convergence_threshold:
                print(f"   🎯 Converged at pass {pass_num}!")
                break
            
            # Stuck detection
            if self.config.allow_stuck_detection and pass_num >= self.config.stuck_after_passes:
                if self._is_stuck():
                    print(f"   ⚠️ Detected stuck pattern, attempting recovery...")
                    best_solution = self._recover_from_stuck(goal, context)
                    break
            
            # Run validation if provided
            if validate_fn and pass_num >= 2:
                validation_result = validate_fn(best_solution)
                if validation_result.get("passed"):
                    print(f"   ✅ Validation passed at pass {pass_num}")
                    break
                else:
                    print(f"   ❌ Validation failed: {validation_result.get('error', 'Unknown')}")
                    context["validation_error"] = validation_result
        
        return {
            "solution": best_solution,
            "passes": [self._pass_to_dict(p) for p in self.passes],
            "num_passes": len(self.passes),
            "convergence_score": best_score,
            "total_duration_ms": sum(p.duration_ms for p in self.passes),
        }
    
    def _get_pass_type(self, pass_num: int, goal: str, context: Dict) -> PassType:
        """Determine the type of pass based on iteration."""
        if pass_num == 1:
            return PassType.RESEARCH  # NEW: Always research first
        elif pass_num == 2:
            return PassType.ANALYSIS
        elif pass_num == 3:
            return PassType.IMPLEMENTATION
        elif pass_num == 4:
            return PassType.VALIDATION
        elif pass_num == 5:
            return PassType.DEBUGGING
        else:
            return PassType.REFLECTION
    
    def _create_pass_prompt(
        self,
        pass_num: int,
        pass_type: PassType,
        goal: str,
        context: Dict[str, Any],
    ) -> str:
        """Create the prompt for this pass WITH skill enrichment."""
        
        # Base prompt with context
        base_prompt = """You are building ENTERPRISE-LEVEL applications. This means:

- PRODUCTION-READY: Code that works out of the box
- FULL-STACK: Backend API + Frontend UI + Database
- STRUCTURED: Proper folder organization (app/, templates/, static/)
- SECURE: Input validation, auth, error handling
- COMPLETE: No TODOs, no placeholders, no "...rest of code"

Task: """ + f"{goal}\n\n"
        
        # NEW: Include active skills context
        if context.get("active_skills"):
            skills_list = ", ".join(context["active_skills"])
            base_prompt += f"🎯 Available skills: {skills_list}\n\n"
        
        if context.get("code_context"):
            base_prompt += f"Code context:\n{context['code_context'][:2000]}\n\n"
        
        if context.get("error"):
            base_prompt += f"Error message:\n{context['error']}\n\n"
        
        if context.get("validation_error"):
            base_prompt += f"Previous validation error:\n{context['validation_error']}\n\n"
        
        # NEW: Include skill hints from orchestrator
        if context.get("skill_hints"):
            base_prompt += f"Skill guidance:\n{context['skill_hints']}\n\n"
        
        # NEW: Include memory context from swarmvault
        if context.get("memory_context"):
            base_prompt += f"Relevant memory:\n{context['memory_context'][:1000]}\n\n"
        
        if self.passes and pass_num > 1:
            base_prompt += f"Previous attempts:\n"
            for i, p in enumerate(self.passes[-2:], max(1, len(self.passes) - 1)):
                base_prompt += f"Pass {i}: {p.response[:500]}...\n"
            base_prompt += "\n"
        
        # Pass-specific instructions
        if pass_type == PassType.RESEARCH:
            return base_prompt + """
RESEARCH PASS - Understanding the Application Domain

CRITICAL: Before building ANY application, you MUST research the topic.

1. Use Tavily search to find information about: """ + goal + """
2. Search GitHub for similar projects
3. Identify key features and tech stack from real implementations
4. Provide a comprehensive research summary

Output your research findings in this format:
```json
{
  "research": {
    "summary": "What is this application about?",
    "key_features": ["feature1", "feature2", ...],
    "tech_stack": ["Python", "Flask", "React", ...],
    "references": ["https://github.com/...", ...]
  }
}
```

If you cannot find specific information, research broadly about the domain.
""" + f"\n\nTOPIC TO RESEARCH: {goal}\n"
        
        elif pass_type == PassType.ANALYSIS:
            return base_prompt + """
ANALYSIS PASS - Understanding the Problem

Think step by step:
1. What is the exact issue or goal?
2. What files are relevant?
3. What is the expected vs actual behavior?
4. What error messages or symptoms exist?
5. What changes are likely needed?

Provide a clear analysis and initial plan.
"""
        
        elif pass_type == PassType.IMPLEMENTATION:
            # Include research context if available
            research_info = ""
            if context.get("research_context"):
                research_info = f"""
RESEARCH CONTEXT (USE THIS TO BUILD THE CORRECT APP):
{context['research_context']}
"""
            
            return base_prompt + research_info + """
IMPLEMENTATION PASS - Creating Enterprise-Level Application

CRITICAL: Build a PRODUCTION-READY, FULL-STACK application based on the research.

1. Use the KEY FEATURES from research to guide your implementation
2. Follow the RECOMMENDED TECH STACK from research
3. Build the ACTUAL application domain, not a generic app

Architecture Requirements:
1. BACKEND: Flask/FastAPI with proper structure
   - app.py or main.py (entry point)
   - models.py (database models)
   - routes/ or endpoints/ (API routes)
   - services/ (business logic)

2. FRONTEND: Modern HTML/CSS/JS
   - templates/ folder with Jinja2 templates
   - static/ folder with CSS, JS
   - Responsive design with CSS Grid/Flexbox

3. DATABASE: SQLite/PostgreSQL with ORM
   - SQLAlchemy models

4. API STRUCTURE:
   - RESTful endpoints (/api/v1/...)
   - JSON request/response
   - Authentication (JWT/Session)

Output JSON with ALL files:

```json
{
  "files": [
    {"path": "app.py", "content": "import flask
from flask import Flask, jsonify, request
# Complete Flask app"},
    {"path": "models.py", "content": "from flask_sqlalchemy import SQLAlchemy
# All models"},
    {"path": "templates/index.html", "content": "<!DOCTYPE html>
<html>
<head><title>App</title></head>
<body>...</body>
</html>"},
    {"path": "static/style.css", "content": "/* Full CSS */"},
    {"path": "static/app.js", "content": "// Complete JS with API calls"},
    {"path": "requirements.txt", "content": "flask
flask-sqlalchemy
flask-cors"},
    {"path": ".env.example", "content": "SECRET_KEY=xxx
DATABASE_URL=sqlite:///app.db"}
  ]
}
```

Rules:
1. EVERY file must be COMPLETE - no TODOs, no placeholders
2. Code must be syntactically correct and runnable
3. Include proper error handling and input validation
4. Use environment variables for secrets
5. Match the domain features from research

Build the complete application now. Output ONLY the JSON block.
"""
        
        elif pass_type == PassType.VALIDATION:
            return base_prompt + """
VALIDATION PASS - Final Code Generation - Build the Actual Application

CRITICAL: Generate COMPLETE, WORKING code files for the task.

OUTPUT FORMAT - STRICT JSON WITH ESCAPED NEWLINES:
You MUST output valid JSON where the "content" field contains ESCAPED newlines (\\n), NOT actual newlines.

```json
{
  "files": [
    {
      "path": "app.py",
      "content": "from flask import Flask\\napp = Flask(__name__)\\n\\n@app.route('/')\\ndef home():\\n    return 'Hello World'\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)"
    },
    {
      "path": "templates/index.html",
      "content": "<!DOCTYPE html>\\n<html>\\n<head><title>Todo App</title></head>\\n<body><h1>My Todos</h1></body>\\n</html>"
    },
    {
      "path": "static/style.css",
      "content": "body { font-family: sans-serif; }\\nh1 { color: #333; }"
    },
    {
      "path": "requirements.txt",
      "content": "flask\\nflask-cors"
    }
  ]
}
```

IMPORTANT: Use \\n for newlines inside the content strings. Do NOT use actual line breaks.

1. For web apps: Create Flask/FastAPI backend with HTML templates
2. Include requirements.txt with all dependencies
3. Output COMPLETE code, not placeholders
4. Use proper directory structure (templates/, static/)

Generate properly formatted code with ESCAPED newlines. Output ONLY the JSON block.
"""
        
        elif pass_type == PassType.DEBUGGING:
            return base_prompt + """
DEBUGGING PASS - Fixing Issues

If validation failed or there are issues:
1. What exactly went wrong?
2. What is the root cause?
3. How will you fix it differently?
4. What did you learn from the failure?

Provide an improved solution.
"""
        
        else:  # REFLECTION
            return base_prompt + """
REFLECTION PASS - Final Review

Final verification:
1. Is the solution complete?
2. Are all tests passing?
3. Any remaining issues?
4. Summary of what was done?

Provide final status and summary.
"""
    
    def _execute_pass(self, prompt: str, context: Dict, pass_type: PassType = None) -> str:
        """Execute a single thinking pass."""
        
        # NEW: For RESEARCH pass, do actual web research
        if pass_type == PassType.RESEARCH and WEB_RESEARCH_AVAILABLE:
            print("🔍 Conducting web research...")
            try:
                researcher = WebResearcher()
                # Extract topic from prompt
                topic = context.get("goal", "")
                if not topic:
                    # Try to extract from prompt
                    import re
                    match = re.search(r"TOPIC TO RESEARCH: (.+)", prompt)
                    if match:
                        topic = match.group(1).strip()
                
                if topic:
                    result = researcher.research(topic, depth="advanced")
                    if result.success:
                        research_context = researcher.build_research_context(result)
                        print(f"✅ Research complete: {len(result.key_features)} features identified")
                        return research_context
                    else:
                        print(f"⚠️ Research failed: {result.error}")
                        return f"Could not research topic. Please provide details about: {topic}"
            except Exception as e:
                print(f"⚠️ Research error: {e}")
                return f"Research error: {str(e)}"
        
        # Normal pass execution - use LLM
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Call with explicit max_tokens to ensure response
            result = self.router.complete(messages, max_tokens=4096, temperature=0.1)
            if "error" in result:
                return f"Error: {result['error']}"
            return result.get("content", "")
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for thinking WITH skill awareness."""
        return """You are Neuro, an expert software engineering AI.

CRITICAL: Output ONLY a JSON code block with ESCAPED newlines (\\\\n), nothing else.

```json
{
  "files": [
    {"path": "app.py", "content": "from flask import Flask\\napp = Flask(__name__)\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)"},
    {"path": "requirements.txt", "content": "flask"}
  ]
}
```

RULE: Inside "content" strings, use \\n for newlines. NOT actual line breaks.

IMPORTANT: If research context was provided in a previous pass, use that information to build the correct application for the domain. Do NOT build generic apps.

Follow this format EXACTLY. Replace content with your actual implementation.
Include complete, working code. No explanations, just the JSON block."""
    
    def _score_convergence(self, new_response: str, best_response: str) -> float:
        """
        Score how close we are to convergence.
        Simple heuristic based on response patterns.
        """
        if not best_response:
            return 0.5
        
        # Count solution indicators
        positive = ["fix", "solution", "implemented", "complete", "verified", "pass", "success"]
        negative = ["error", "fail", "issue", "problem", "not sure", "cannot"]
        
        new_lower = new_response.lower()
        best_lower = best_response.lower()
        
        new_pos = sum(1 for w in positive if w in new_lower)
        new_neg = sum(1 for w in negative if w in new_lower)
        best_pos = sum(1 for w in positive if w in best_lower)
        best_neg = sum(1 for w in negative if w in best_lower)
        
        # Score based on positive/negative ratio
        if new_pos + new_neg == 0:
            return 0.5
        
        new_score = new_pos / (new_pos + new_neg)
        best_score = best_pos / (best_pos + best_neg) if best_pos + best_neg > 0 else 0.5
        
        # Convergence means similar high score
        return (new_score + best_score) / 2
    
    def _is_stuck(self) -> bool:
        """Detect if we're stuck in a loop."""
        # Disabled - let all passes complete naturally
        return False
    
    def _recover_from_stuck(self, goal: str, context: Dict) -> str:
        """Recover from being stuck."""
        recovery_prompt = f"""I'm stuck on this task: {goal}

Previous attempts haven't converged. Try a different approach:

1. Re-read the original problem
2. Consider if there's a simpler solution
3. Try breaking down the problem differently

IMPORTANT: Output complete, working code as JSON:
```json
{{
  "files": [
    {{"path": "app.py", "content": "FULL Python code"}},
    {{"path": "templates/index.html", "content": "FULL HTML"}},
    {{"path": "static/style.css", "content": "FULL CSS"}}
  ]
}}
```

Output ONLY JSON block with complete files.
"""
        
        messages = [{"role": "user", "content": recovery_prompt}]
        
        try:
            result = self.router.complete(messages, temperature=0.3)
            return result.get("content", "Could not recover")
        except:
            return "Recovery failed"
    
    def _pass_to_dict(self, p: ThinkingPass) -> Dict:
        """Convert ThinkingPass to dict."""
        return {
            "type": p.pass_type.value,
            "duration_ms": p.duration_ms,
            "success": p.success,
            "response_preview": p.response[:500] if p.response else "",
            "metadata": p.metadata,
        }
    
    def get_summary(self) -> str:
        """Get a summary of the thinking loop."""
        if not self.passes:
            return "No passes completed"
        
        summary = f"Thinking Loop Summary:\n"
        summary += f"- Total passes: {len(self.passes)}\n"
        summary += f"- Convergence score: {self.convergence_score:.2f}\n"
        summary += f"- Total duration: {sum(p.duration_ms for p in self.passes)/1000:.1f}s\n"
        
        for i, p in enumerate(self.passes, 1):
            status = "✓" if p.success else "✗"
            summary += f"  Pass {i} ({p.pass_type.value}): {status} - {p.duration_ms/1000:.1f}s\n"
        
        return summary


def run_thinking_loop(
    router,
    goal: str,
    context: Optional[Dict[str, Any]] = None,
    max_passes: int = 6,
) -> Dict[str, Any]:
    """
    Convenience function to run a thinking loop.
    
    Usage:
        from neuro.reasoning.thinking_loop import run_thinking_loop
        from neuro.router import smart_router
        
        result = run_thinking_loop(
            router=smart_router,
            goal="Fix the login bug",
            max_passes=4
        )
        
        print(result["solution"])
    """
    config = LoopConfig(max_passes=max_passes)
    loop = ThinkingLoop(router, config)
    return loop.run(goal, context)
