# CODEX PROMPT: Neuro Autonomous Agent System Improvement

## CONTEXT: What is Neuro?

Neuro is an autonomous AI agent that builds enterprise applications, websites, and software based on user goals. It uses multi-agent orchestration (Planner → Coder → Reviewer → Executor) with 78+ skills and multiple AI model providers.

**Latest commit:** `a208ff47d3337746700456305118e13334176602`

---

## CURRENT ARCHITECTURE (DO NOT CHANGE)

### Models (Free Tier Only - Working)
- **Groq**: 5 keys working, `llama-3.1-8b-instant` functional
- **Gemini**: 8 keys exist but rate-limited (quota exhausted on free tier)
- **OpenRouter**: 4 keys but rate-limited on free models

### Core Components
```
neuro/
├── __main__.py          # CLI entry point
├── models.py            # 56 models registered (FREE tier)
├── router/
│   ├── smart_router.py  # Multi-provider LLM router
│   ├── scenario_router.py
│   └── task_router.py
├── executor/
│   ├── agent_loop.py    # Main agent loop (4-role swarm)
│   └── role_agents.py   # Agent swarm implementation
├── reasoning/
│   ├── thinking_loop.py # Multi-pass reasoning
│   ├── chain_of_thought.py
│   ├── prompt_writer.py # AI-powered prompt enhancement
│   └── web_researcher.py
├── core/
│   └── code_parser.py   # JSON → file extraction
├── control/            # NEW: 3-tier control loops
│   ├── control_loop.py
│   ├── checkpoint.py
│   └── mcp_client.py
├── skills/             # 78 skills
│   ├── enterprise_app_builder.py
│   ├── website_builder.py
│   ├── frontend_builder.py
│   └── ... (74 more)
└── validation/
    └── test_runner.py
```

---

## PROBLEMS IDENTIFIED

### 1. CRITICAL: JSON Parsing Failure
**Symptom:** Files created have 0 bytes
**Location:** `neuro/core/code_parser.py`
**Issue:** LLM outputs JSON with actual newlines inside string values (invalid JSON), parser fails to extract content

```
Example bad output:
{
  "path": "app.py",
  "content": "import os
from flask import Flask
..."
}
```

**Current strategies (not working reliably):**
- Strategy 1: Strict JSON parsing
- Strategy 2: Flexible JSON with newline fixing
- Strategy 3: Code block extraction
- Strategy 4: Embedded JSON-like extraction

### 2. CRITICAL: File Writing Sometimes Fails
**Symptom:** Parser returns file paths but files are empty (0 bytes)
**Location:** `neuro/executor/agent_loop.py` lines 371-386
**Issue:** Content extraction from JSON fails silently

### 3. WEB RESEARCH PARTIALLY BROKEN
**Tavily API:** Not working (invalid key / rate limit)
**GitHub research:** Working
**Browser fallback:** Limited due to CAPTCHAs

### 4. LLM OUTPUT QUALITY
**Issue:** Models sometimes output:
- Very short code (incomplete files)
- Code without proper structure
- JSON without required fields
- Content truncated mid-file

### 5. MISSING: Enterprise-Level Features
- No proper project scaffolding
- No dependency management
- No build verification
- No error recovery mid-build
- Limited multi-file coordination

---

## WHAT WORKS (Preserve These)

✅ SmartRouter multi-provider routing
✅ Agent swarm (4 roles working)
✅ Thinking loop with passes
✅ Skill registry (78 skills)
✅ Control loops (newly added)
✅ Checkpoint system (newly added)
✅ GitHub research (works)
✅ Groq API (working with 5 keys)

---

## REQUIREMENTS FOR CODEX

### 1. FIX JSON PARSING (HIGHEST PRIORITY)

The code parser MUST handle these cases:

**Case A: Actual newlines in JSON values**
```json
{
  "files": [
    {
      "path": "app.py",
      "content": "import os
from flask import Flask
app = Flask(__name__)
..."
    }
  ]
}
```

**Case B: Escaped newlines**
```json
{
  "files": [
    {
      "path": "app.py",
      "content": "import os\\nfrom flask import Flask\\napp = Flask(__name__)\\n..."
    }
  ]
}
```

**Case C: Triple-quoted content**
```json
{
  "files": [
    {
      "path": "app.py",
      "content": "\"\"\"import os\nfrom flask import Flask\n...\"\"\""
    }
  ]
}
```

**Case D: Code blocks without JSON**
````
```python
# filename: app.py
import os
from flask import Flask
...
```
````

**Case E: Plain text with filenames**
```
app.py:
import os
from flask import Flask

models.py:
from flask_sqlalchemy import SQLAlchemy
```

### 2. IMPROVE FILE WRITING

After parsing, verify files have content:
```python
# MUST verify after writing
for f in files_created:
    size = os.path.getsize(f)
    if size == 0:
        # Retry extraction or mark as failed
        pass
```

### 3. ADD ALTERNATIVE WEB RESEARCH

When Tavily fails, use:
- GitHub search (already working)
- DuckDuckGo API (free)
- SerpAPI (free tier)
- Direct URL crawling

### 4. ADD PROJECT SCAFFOLDING

For enterprise apps, generate:
```
project/
├── src/
├── tests/
├── docs/
├── docker-compose.yml
├── .env.example
├── package.json (if Node)
├── requirements.txt (if Python)
├── README.md
└── SPEC.md
```

### 5. ADD BUILD VERIFICATION

After generating files:
1. Check syntax (python -m py_compile)
2. Check dependencies (pip install -r requirements.txt --dry-run)
3. Run basic tests
4. Report what works / what doesn't

### 6. ADD ERROR RECOVERY

When a pass fails:
1. Try alternative model
2. Try simplified prompt
3. Try partial implementation
4. Log what failed and why

---

## FREE RESOURCES TO INTEGRATE

### APIs (No Card Required)
1. **GitHub API** - Already integrated
2. **DuckDuckGo API** - Free, no auth needed
3. **HuggingFace Inference API** - Free tier available
4. **Cerebras** - 90K tokens/day free
5. **Together AI** - Free models available

### Libraries to Consider
1. **json-repair** - Fix malformed JSON
2. **python-dotenv** - Environment management
3. **playwright** - Browser automation (already partially integrated)
4. **instructor** - Structured output from LLMs

### GitHub Repos to Reference
1. **SWE-agent** - Agentic coding patterns
2. **PraisonAI** - Multi-agent framework
3. **agenticSeek** - Browser+MCP integration
4. **cursor** - Code editing patterns

---

## PROHIBITED CHANGES

❌ DO NOT remove or change Groq models
❌ DO NOT remove or change Gemini models
❌ DO NOT remove or change OpenRouter models
❌ DO NOT change the model registry structure
❌ DO NOT remove the skill registry
❌ DO NOT change the agent swarm architecture
❌ DO NOT add paid APIs without user consent
❌ DO NOT commit API keys to GitHub

---

## OUTPUT FORMAT

When providing fixes, include:
1. File path(s) to modify
2. Specific code changes (before/after)
3. Testing instructions
4. Any new dependencies (must be pip installable, free)

---

## EXAMPLE IMPROVEMENT REQUEST

"Fix the JSON parsing in neuro/core/code_parser.py to handle actual newlines in string values. The current _fix_json_newlines method doesn't work correctly. Test with this input: [example JSON with newlines]"

---

## CURRENT TEST COMMAND

```bash
# Test SmartRouter
python -c "from neuro.router.smart_router import SmartRouter; r = SmartRouter(); print(r.health_check())"

# Test full build
PYTHONPATH=. python -m neuro --goal "Build a todo app" --working-dir ./test_output --apply
```

---

## KEY FILES TO EXAMINE

1. `neuro/core/code_parser.py` - JSON parsing (PROBLEM)
2. `neuro/executor/agent_loop.py` - File writing (PROBLEM)
3. `neuro/reasoning/web_researcher.py` - Web research (PARTIAL)
4. `neuro/router/smart_router.py` - LLM calls (WORKING)
5. `neuro/models.py` - Model registry (PRESERVE)

---

End of context. Make improvements that enable Neuro to build enterprise-level applications reliably.
