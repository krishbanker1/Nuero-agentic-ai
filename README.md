# Neuro - Autonomous Coding System

An intelligent multi-model routing agent system with automatic skill integration.
Neuro is a brain-inspired autonomous engineering runtime designed to build production-grade apps.

## ⚠️ HONEST STATUS

**Current Status**: Neuro has a working core loop for autonomous coding.

**What's Real**:
- ✅ Multi-provider model routing (Groq, OpenRouter, Gemini, Together, HuggingFace, Cloudflare)
- ✅ 50+ model registry with structured metadata and role-based selection
- ✅ Staged cognitive routing (planner → coder → debugger → validator)
- ✅ Structured edit format for machine-parseable file changes
- ✅ Command execution with validation
- ✅ Error repair loop
- ✅ Local smoke-eval harness for quality checks
- ✅ Safe file writing with workspace boundary enforcement

**What's NOT Claimed**:
- ❌ Paid or card-required provider access
- ❌ Unsupported competitive claims
- ❌ Guaranteed production readiness without running validation checks

**Target**: Build production-grade applications with a free-first autonomous engineering workflow.

## Architecture

### Core Loop
```
Task intake → Repo scan → Planning → File selection → Structured edit generation
    → Safe file writing → Command execution → Test/build validation
    → Error analysis → Repair loop → Final diff summary
```

### Model System
- **50+ models** across 8+ providers
- **Role-based routing**: Planner, Architect, Coder, Debugger, Validator, Reviewer, Frontend, Documentation
- **Fallback chains**: Primary model → same provider next key → different provider → generic fallback
- **Free-first execution**: Prioritizes free models before paid
- **Key rotation**: Supports comma-separated multi-key configuration

### Supported Providers
| Provider | Models | Key Env Vars |
|----------|--------|--------------|
| Groq | 6 | GROQ_API_KEY, GROQ_API_KEYS |
| OpenRouter | 20+ | OPENROUTER_API_KEY, OPENROUTER_API_KEYS |
| Gemini | 5 | GEMINI_API_KEY, GEMINI_API_KEYS, GOOGLE_API_KEY |
| Together | 5 | TOGETHER_API_KEY, TOGETHER_API_KEYS |
| HuggingFace | 5 | HF_TOKEN, HUGGINGFACE_API_KEY |
| Cloudflare | 3 | CLOUDFLARE_AI_API_TOKEN |

Note: Qwen and DeepSeek models are accessed via OpenRouter keys.

## Features

- **Smart Router**: Routes tasks to 50+ AI models based on task type and role
- **Structured Edit Format**: Machine-parseable JSON for file changes
- **Safe File Writer**: Workspace boundary enforcement, backup, dry-run mode
- **Command Runner**: Captures stdout/stderr, timeout, dangerous command blocking
- **Error Repair Loop**: Analyzes failures, generates fixes, re-validates
- **Memory System**: Stores task history, model performance, fallback events
- **Smoke Eval Harness**: Local smoke tests for autonomous coding capability


### Production App Builder Layer

Neuro now adds deterministic structure before asking the current free models to write code:

- **ProductionScaffolder** chooses a local/free scaffold for full-stack apps, APIs, websites, presentations, or Python packages.
- **ProductionBuildPipeline** splits generation into spec, backend/data, frontend, and tests/deployment stages.
- Each stage includes required files, validation commands, and targeted repair prompts so small/free models can work on smaller verified slices.
- Quality gates require non-empty files, local run/test instructions, no paid/card-required services, and no hardcoded secrets.

This keeps the existing model/provider configuration as the brain while adding stronger deterministic engineering scaffolding around it.


## Installation

Neuro has a small default install so it can boot on a fresh/free machine without pulling heavy optional runtimes.

```bash
# Core CLI/runtime
pip install -e .

# Both spellings work after install:
#   neuro --health
#   nuero --health

# Provider SDKs for the configured model brain (Groq, Gemini, OpenRouter/OpenAI-compatible, etc.)
pip install -e ".[providers]"

# Optional visual/browser/research/memory extras
pip install -e ".[visual,browser,research,memory]"
```

The install no longer depends on the invalid `sqlitevec` package name. Vector-memory support is optional and uses the published `sqlite-vec` package when the `memory` extra is requested. Browser and visual-analysis packages are also optional; Neuro keeps running without them and only asks for the relevant extra when that feature is used.


### Execution mode

Neuro applies validated changes by default so it can actually build files in the target workspace. Use `--dry-run` only when you want a preview that does not write code.

```bash
neuro --goal "Build a landing page"          # writes validated changes
neuro --goal "Build a landing page" --dry-run # preview only
```

Optional extras do not remove capabilities from Neuro. They keep fresh installs from failing on heavyweight packages; when a task needs provider SDKs, browser automation, visual analysis, research, or vector memory, install the matching extra shown above.

## Usage

### Basic Autonomous Coding
```python
from neuro.tools import AutonomousEditLoop, parse_structured_edit

# Create edit loop
loop = AutonomousEditLoop("/path/to/project", dry_run=False)

# Parse model's structured edit
edit, errors = parse_structured_edit(model_response)

# Apply and validate
result = loop.execute_and_validate(edit)
```

### Router Usage
```python
from neuro.router.smart_router import SmartRouter, Provider

router = SmartRouter()
result = router.complete(
    messages=[{"role": "user", "content": "Fix the bug"}],
    model="openrouter/qwen/qwen3-coder:free"
)
```

### Model Registry
```python
from neuro.models import (
    MODEL_REGISTRY,
    get_models_by_role,
    get_free_models,
    ModelRole,
)

# Get coder models sorted by priority
coders = get_models_by_role(ModelRole.CODER)

# Get all free models
free_models = get_free_models()
```

### Smoke Eval Harness
```python
from neuro.validation.mini_eval import run_mini_evals

# Run local smoke checks
summary = run_mini_evals()
print(f"Passed: {summary['passed']}/{summary['total']}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_neuro_fixes.py -v

# Run smoke evals
python -m neuro.validation.mini_eval
```

## Environment Variables

```bash
# Required for providers (at least one needed)
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Multiple keys (comma-separated)
GROQ_API_KEYS=key1,key2,key3

# Optional providers
TOGETHER_API_KEY=your_key
HF_TOKEN=your_token
CLOUDFLARE_AI_API_TOKEN=your_token
```

## License

MIT
