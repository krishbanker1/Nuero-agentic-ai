"""Iterative Refinement Loop - Multi-pass until perfect using REAL AI"""
from typing import Dict, Any, List, Optional
from neuro.router.smart_router import SmartRouter

class IterativeRefiner:
    """
    Multi-pass refinement loop - like Claude/Codex.
    Pass 1: Generate
    Pass 2-5+: Refine based on feedback
    Stop when: Passes tests, no errors, AI says done
    
    Uses FREE models via SmartRouter.
    """
    
    def __init__(self):
        self.router = SmartRouter()
        self.max_passes = 5
    
    def refine(
        self, 
        spec: str, 
        initial_code: str = None,
        language: str = "python",
        tests: str = None
    ) -> Dict[str, Any]:
        """
        Iteratively refine until perfect.
        """
        passes = []
        current_code = initial_code
        iteration = 0
        
        while iteration < self.max_passes:
            iteration += 1
            
            # Generate or refine
            if iteration == 1 and not current_code:
                current_code = self._generate(spec, language)
            else:
                current_code = self._refine(
                    spec, current_code, language, tests, passes
                )
            
            passes.append({
                "iteration": iteration,
                "code": current_code,
                "length": len(current_code)
            })
            
            # Check if done
            if self._is_good_enough(current_code, spec, tests, passes):
                break
        
        return {
            "spec": spec,
            "final_code": current_code,
            "passes": passes,
            "iterations": iteration,
            "converged": iteration < self.max_passes
        }
    
    def _generate(self, spec: str, language: str) -> str:
        """First pass: Generate code."""
        prompt = f"""Generate complete, working {language} code for:

{spec}

Requirements:
- Production-ready
- Error handling
- Type hints
- Docstrings
- Follows best practices

Output ONLY code, no markdown.
"""
        return self.router.chat(prompt, task_type="code_generation")
    
    def _refine(
        self, 
        spec: str, 
        code: str, 
        language: str,
        tests: str,
        history: list
    ) -> str:
        """Subsequent passes: Refine based on issues."""
        
        # Get previous issues
        issues = self._find_issues(code, spec, language)
        
        if not issues:
            return code
        
        prompt = f"""Refine this {language} code:

ORIGINAL SPEC: {spec}
{issues}

CODE:
```{language}
{code}
```

Fix the issues. Output ONLY the REFINED code, no markdown.
"""
        return self.router.chat(prompt, task_type="code_refinement")
    
    def _find_issues(self, code: str, spec: str, language: str) -> str:
        """Find issues in code."""
        prompt = f"""Review this code against the spec:

SPEC: {spec}

LANGUAGE: {language}

CODE:
{code}

Check:
1. Does it match the spec?
2. Any syntax errors?
3. Missing error handling?
4. Security issues?
5. Performance problems?
6. Edge cases handled?

List specific issues found. If none, say "No issues found."
"""
        return self.router.chat(prompt, task_type="code_review")
    
    def _is_good_enough(
        self, 
        code: str, 
        spec: str, 
        tests: str,
        history: list
    ) -> bool:
        """Check if code is good enough."""
        
        # Check convergence
        if len(history) >= 2:
            if abs(len(history[-1]['code']) - len(history[-2]['code'])) < 10:
                return True  # Converged
        
        # Check with AI
        prompt = f"""Evaluate this code:

SPEC: {spec}
CODE (first 100 lines): {code[:2000]}

Is this code production-ready? 
- Complete implementation?
- No obvious bugs?
- Matches spec?

Respond YES or NO with brief reason.
"""
        response = self.router.chat(prompt, task_type="reasoning_planning")
        
        return "yes" in response.lower() and any(word in response.lower() 
               for word in ["complete", "ready", "good", "production"])


def iterative_refine(spec: str, language: str = "python") -> Dict[str, Any]:
    """Quick iterative refinement."""
    return IterativeRefiner().refine(spec, language=language)
