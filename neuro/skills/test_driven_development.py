"""Test-Driven Development - TDD cycle using REAL AI"""
from typing import Dict, Any
from neuro.router.smart_router import SmartRouter

class TestDrivenDevelopment:
    """Write tests first, then code."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def write_tests(self, spec: str, language: str = "python") -> Dict[str, str]:
        """Write tests BEFORE code (RED phase)."""
        
        prompt = f"""Write FAILING tests for this feature specification (RED phase of TDD):

SPEC: {spec}

Write tests that:
- Test the expected behavior
- Cover happy path AND edge cases
- Are specific and deterministic

Output test code only. Make tests fail to prove they're testing something real.
"""
        
        tests = self.router.chat(prompt, task_type="testing")
        
        return {
            "tests": tests,
            "phase": "RED",
            "spec": spec,
            "language": language
        }
    
    def write_code(self, tests: str, spec: str, language: str = "python") -> str:
        """Write MINIMAL code to pass tests (GREEN phase)."""
        
        prompt = f"""Write MINIMAL code to make these tests pass (GREEN phase of TDD):

SPEC: {spec}

TESTS:
{tests}

Write ONLY the code needed to pass tests. Don't over-engineer. Output code only.
"""
        
        return self.router.chat(prompt, task_type="code_generation")
    
    def refactor(self, code: str, tests: str, language: str = "python") -> str:
        """Refactor while keeping tests green (REFACTOR phase)."""
        
        prompt = f"""Refactor this code while keeping tests passing (REFACTOR phase of TDD):

CODE:
{code}

TESTS:
{tests}

Improve:
- Readability
- Structure
- Remove duplication

Output refactored code. Tests must still pass.
"""
        
        return self.router.chat(prompt, task_type="code_simplification")
    
    def full_tdd_cycle(self, spec: str, language: str = "python") -> Dict[str, Any]:
        """Run complete TDD cycle."""
        tests = self.write_tests(spec, language)
        code = self.write_code(tests["tests"], spec, language)
        refactored = self.refactor(code, tests["tests"], language)
        
        return {
            "spec": spec,
            "red_tests": tests,
            "green_code": code,
            "refactored_code": refactored
        }


def tdd_cycle(spec: str, language: str = "python") -> Dict[str, Any]:
    """Quick TDD cycle."""
    return TestDrivenDevelopment().full_tdd_cycle(spec, language)
