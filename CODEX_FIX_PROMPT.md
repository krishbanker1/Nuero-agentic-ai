# Neuro Codebase Fixes for Codex

Fix these issues in order. Test after each fix.

---

## FIX 1: Add Missing Dependencies to pyproject.toml

**File:** `/workspace/project/Nuero-agentic-ai/pyproject.toml`

**Problem:** Missing dependencies for visual analysis and other features.

**Current dependencies:**
```toml
dependencies = [
    "groq>=0.4.0",
    "openai>=1.0.0",
    "json-repair>=0.39.0",
]
```

**Fix:** Add these dependencies:

```toml
dependencies = [
    "groq>=0.4.0",
    "openai>=1.0.0",
    "json-repair>=0.39.0",
    # Visual analysis (for cinematic_design skill)
    "yt-dlp>=2024.0.0",
    "opencv-python>=4.9.0",
    "Pillow>=10.0.0",
    "numpy>=1.24.0",
    "requests>=2.31.0",
    # Browser automation
    "playwright>=1.40.0",
    # Memory & persistence
    "chromadb>=0.4.0",
    "sqlitevec>=0.0.0",
    # Enhanced browser
    "beautifulsoup4>=4.12.0",
    "html2text>=2020.1.16",
    # Shell execution
    "python-dotenv>=1.0.0",
]
```

---

## FIX 2: Deduplicate MODEL_REGISTRY in neuro/models.py

**File:** `/workspace/project/Nuero-agentic-ai/neuro/models.py`

**Problem:** Model entries are duplicated multiple times.

**Find and remove duplicates:**
- Search for `groq/llama-3.3-70b-versatile` - appears 3+ times
- Search for any model appearing more than once
- Keep ONE entry per model, keep the BEST metadata

**Before:**
```python
ModelMetadata(
    name="groq/llama-3.3-70b-versatile",
    provider="groq",
    roles=["planner", "architect", "coder", "debugger", "refactor"],
    strengths=["fast", "reasoning", "code", "long-context"],
    priority=1,
    ...
),
# ... same model appears AGAIN later with different comment
ModelMetadata(
    name="groq/llama-3.3-70b-versatile",  # DUPLICATE!
    provider="groq",
    ...
)
```

**After:** Each model should appear exactly ONCE.

**How to fix:**
1. Read through MODEL_REGISTRY
2. Remove exact duplicates (same name AND provider)
3. Keep the entry with the MOST complete metadata
4. Verify no model appears twice

---

## FIX 3: Verify and Fix Lazy Import Paths

**File:** `/workspace/project/Nuero-agentic-ai/neuro/skills/__init__.py`

**Problem:** Some lazy import paths may be wrong or point to non-existent classes.

**Current lazy imports:**
```python
_lazy_imports = {
    "react_three_fiber": "neuro.skills.react_three_fiber.ReactThreeFiber",
    "threejs_core": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",  # Check this
    "threejs": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",
    "webgl": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",
    "spline_design": "neuro.skills.spline_design.SplineDesign",
    "glsl_shaders": "neuro.skills.glsl_shaders.GLSLShaders",
    ...
}
```

**Fix:** For EACH lazy import:
1. Find the actual file path
2. Open that file
3. Find the actual class name
4. Verify the path and class exist

**Common issues to fix:**
- Wrong class name (typos)
- File doesn't exist
- Class renamed/moved

---

## FIX 4: Add API Key Validation

**File:** `/workspace/project/Nuero-agentic-ai/neuro/router.py`

**Problem:** If API keys are missing, system fails silently.

**Current code:**
```python
GEMINI_KEYS = _get_env_keys("GEMINI_API_KEYS")
if not GEMINI_KEYS:
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        GEMINI_KEYS = [key]
# Silent failure if no keys!
```

**Fix:** Add validation:
```python
def validate_keys():
    """Validate that at least one provider has keys."""
    gemini = bool(GEMINI_KEYS)
    groq = bool(GROQ_KEYS)
    openrouter = bool(OPENROUTER_KEYS)
    
    if not any([gemini, groq, openrouter]):
        raise RuntimeError(
            "No API keys found! Set at least one of:\n"
            "  - GEMINI_API_KEY\n"
            "  - GROQ_API_KEY\n"
            "  - OPENROUTER_API_KEY"
        )
    
    return {"gemini": gemini, "groq": groq, "openrouter": openrouter}

# Call on module load
_validate = validate_keys()
```

---

## FIX 5: Add Type Hints to Critical Functions

**Files:** 
- `neuro/skills/cinematic_design.py`
- `neuro/router.py`
- `neuro/executor/agent_loop.py`

**Problem:** Missing type hints make code hard to maintain.

**Fix:** Add `# type:` hints or `from __future__ import annotations` at top.

Example for `neuro/router.py`:
```python
from __future__ import annotations
from typing import List, Optional, Dict, Any

def complete(role: str, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
    ...
```

---

## FIX 6: Add Startup Health Check

**File:** `/workspace/project/Nuero-agentic-ai/neuro/__init__.py`

**Problem:** No way to verify system is properly configured.

**Add this function:**
```python
def health_check() -> dict[str, Any]:
    """Verify Neuro is properly configured."""
    from neuro.router import available_providers, has_provider
    from neuro.models import MODEL_REGISTRY
    
    issues = []
    
    # Check API keys
    providers = available_providers()
    if not any(providers.values()):
        issues.append("No API keys configured")
    
    # Check models
    enabled_models = [m for m in MODEL_REGISTRY if m.enabled]
    if not enabled_models:
        issues.append("No enabled models")
    
    return {
        "status": "healthy" if not issues else "degraded",
        "providers": providers,
        "model_count": len(enabled_models),
        "issues": issues
    }

__all__.append("health_check")
```

---

## FIX 7: Add Tests for Critical Paths

**Files to test:**
- `neuro/skills/cinematic_design.py` - Already exists
- `neuro/router.py` - Needs test
- `neuro/executor/agent_loop.py` - Needs test

**Create test file: `tests/test_router.py`**
```python
"""Tests for neuro/router.py"""
import pytest
from neuro.router import complete, has_provider, available_providers

def test_available_providers():
    """Test provider detection."""
    result = available_providers()
    assert isinstance(result, dict)
    assert "gemini" in result
    assert "groq" in result
    assert "openrouter" in result

def test_has_provider():
    """Test provider key checking."""
    # Should return bool
    result = has_provider("gemini")
    assert isinstance(result, bool)
```

---

## FIX 8: Fix Circular Import in __init__.py

**File:** `/workspace/project/Nuero-agentic-ai/neuro/__init__.py`

**Problem:** Potential circular imports.

**Current structure:**
```python
from neuro.executor.agent_loop import create_agent, run_goal, ...
from neuro.skills import SkillAutomation, get_skill_manager, ...
from neuro.product import ProductSpec, ...
# imports cascade into many submodules
```

**Fix:** Add circular import guard:
```python
# At the TOP of neuro/__init__.py
from __future__ import annotations
```

And in submodules that import from neuro:
```python
# Instead of "from neuro import X"
# Use "from neuro.module import X" directly
# Or lazy import inside functions
```

---

## FIX 9: Add Missing Skill invoke() Methods

**Problem:** Some skills may be missing the `invoke()` classmethod.

**Check each skill has:**
```python
@classmethod
def invoke(cls, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Entry point for SkillOrchestrator."""
    skill = cls()
    result = skill.build_from_input(task, context)
    return {
        "success": True,
        "result": result,
        "skill": cls.NAME,
    }
```

**List of skills to verify:**
- `cinematic_design.py` ✅ has invoke
- Check others in `neuro/skills/*.py`

---

## FIX 10: Add .gitignore Entries

**File:** `/workspace/project/Nuero-agentic-ai/.gitignore`

**Add these:**
```
# Visual analysis temp files
cinematic_*/
*.jpg
*.png
*.mp4
*.webm

# Memory database
*.db
*.sqlite
chromadb/

# Environment
.env.local
.env.production

# Logs
logs/
*.log

# Cache
__pycache__/
*.pyc
.pytest_cache/

# IDE
.vscode/
.idea/
```

---

## PRIORITY ORDER

Do fixes in this order:

1. **FIX 1** - Dependencies (unblocks other fixes)
2. **FIX 2** - Deduplication (cleaner code)
3. **FIX 4** - Key validation (prevents silent failures)
4. **FIX 3** - Lazy imports (prevents runtime crashes)
5. **FIX 5** - Type hints (code quality)
6. **FIX 6** - Health check (debugging)
7. **FIX 7** - Tests (verify fixes)
8. **FIX 8** - Circular imports (stability)
9. **FIX 9** - Skill invoke (consistency)
10. **FIX 10** - .gitignore (clean repo)

---

## VERIFICATION

After all fixes, run:
```bash
cd /workspace/project/Nuero-agentic-ai

# 1. Install dependencies
pip install -e .

# 2. Run tests
python -m pytest tests/ -v

# 3. Check imports
python -c "import neuro; print(neuro.health_check())"

# 4. Verify skills load
python -c "from neuro.skills import get_skill_manager; sm = get_skill_manager(); print(sm.list_skills()[:5])"
```

---

## DO NOT CHANGE

- `neuro/skills/cinematic_design.py` - Already correct
- `neuro/executor/agent_loop.py` - Core logic is fine
- `neuro/models.py` structure - Just fix duplicates
- Root README and docs

---

## END OF FIX PROMPT
