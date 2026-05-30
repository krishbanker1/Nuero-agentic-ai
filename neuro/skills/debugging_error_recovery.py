"""Debugging & Error Recovery - Systematic root-cause debugging using REAL AI"""
from typing import Dict, Any
from neuro.router.smart_router import SmartRouter

class DebuggingErrorRecovery:
    """Systematic debugging with structured triage."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def diagnose(self, error: str, context: str = "") -> Dict[str, Any]:
        """Diagnose error using structured triage."""
        
        prompt = f"""As an expert debugger, diagnose this error using systematic triage:

ERROR:
{error}

CONTEXT:
{context}

Follow the triage checklist:
1. REPRODUCE - Can you reliably reproduce it?
2. ISOLATE - What's the minimal failing case?
3. HYPOTHESIZE - What's causing it?
4. TEST - Verify the hypothesis
5. FIX - Apply the fix
6. VERIFY - Confirm it works

For each step provide:
- What to check
- What to try
- Expected result

Output structured diagnosis.
"""
        
        result = self.router.chat(prompt, task_type="debugging")
        
        return {
            "error": error,
            "diagnosis": result,
            "steps": ["reproduce", "isolate", "hypothesize", "test", "fix", "verify"]
        }
    
    def suggest_fix(self, error: str, code: str) -> str:
        """Get specific fix suggestion."""
        prompt = f"""Fix this error in the code:

ERROR: {error}

CODE:
{code}

Provide the FIXED code. Output only the code, no markdown.
"""
        return self.router.chat(prompt, task_type="debugging")
    
    def reproduce(self, code: str, error: str) -> str:
        """Generate reproduction steps."""
        prompt = f"""Create a minimal reproduction for this bug:

ERROR: {error}

CODE:
{code}

Output bash commands to reproduce the issue.
"""
        return self.router.chat(prompt, task_type="debugging")


def diagnose_error(error: str, context: str = "") -> Dict[str, Any]:
    """Quick error diagnosis."""
    return DebuggingErrorRecovery().diagnose(error, context)
