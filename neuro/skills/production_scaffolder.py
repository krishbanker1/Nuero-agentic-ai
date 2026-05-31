"""Free-first deterministic scaffolding for production app builds.

This module gives Neuro a no-cost structure layer around the current models. The
models still provide the domain-specific code, but the scaffold plan makes their
output smaller, safer, and easier to validate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class ScaffoldFile:
    """A file Neuro should create or fill for a production app."""

    path: str
    purpose: str
    required: bool = True


@dataclass(frozen=True)
class ScaffoldPlan:
    """Deterministic project blueprint for a requested app."""

    stack: str
    description: str
    files: List[ScaffoldFile]
    validation_commands: List[str]
    quality_gates: List[str]
    notes: List[str] = field(default_factory=list)

    def required_paths(self) -> List[str]:
        """Return required paths in generation order."""
        return [file.path for file in self.files if file.required]

    def to_context(self) -> Dict[str, Any]:
        """Return a prompt-friendly dictionary."""
        return {
            "stack": self.stack,
            "description": self.description,
            "required_files": [file.__dict__ for file in self.files],
            "validation_commands": self.validation_commands,
            "quality_gates": self.quality_gates,
            "notes": self.notes,
        }

    def to_prompt_block(self) -> str:
        """Render concise instructions for the thinking loop."""
        file_lines = "\n".join(
            f"- {file.path}: {file.purpose}" for file in self.files
        )
        command_lines = "\n".join(f"- {cmd}" for cmd in self.validation_commands)
        gate_lines = "\n".join(f"- {gate}" for gate in self.quality_gates)
        note_lines = "\n".join(f"- {note}" for note in self.notes)
        return (
            f"Production scaffold: {self.stack}\n"
            f"Purpose: {self.description}\n\n"
            f"Required files:\n{file_lines}\n\n"
            f"Validation commands:\n{command_lines}\n\n"
            f"Quality gates:\n{gate_lines}\n\n"
            f"Notes:\n{note_lines}"
        )


class ProductionScaffolder:
    """Choose deterministic free-first scaffolds for common app requests."""

    COMMON_GATES = [
        "Every generated file must be non-empty and domain-specific.",
        "No paid APIs, hosted subscriptions, or card-required services.",
        "Include README.md, SPEC.md, .env.example, and local run commands.",
        "Use local/open-source dependencies only; keep secrets out of source.",
        "Prefer small validated files over one huge generated file.",
    ]

    @classmethod
    def infer_stack(cls, goal: str, context: Dict[str, Any] | None = None) -> str:
        """Infer the safest scaffold from the user's goal and scenario context."""
        context = context or {}
        goal_lower = goal.lower()
        scenario = str(context.get("scenario") or context.get("task_type") or "").lower()

        if any(word in goal_lower for word in ["presentation", "slides", "deck", "pitch deck"]):
            return "presentation_deck"
        if any(word in goal_lower for word in ["api", "rest", "endpoint", "backend"]):
            return "fastapi_service"
        if any(word in goal_lower for word in ["landing", "portfolio", "static website", "marketing"]):
            return "static_site"
        if "web_app" in scenario or any(word in goal_lower for word in ["website", "dashboard", "saas", "crm", "admin", "enterprise", "full stack", "full-stack"]):
            return "fullstack_fastapi_static"
        return "python_package"

    @classmethod
    def create_plan(cls, goal: str, context: Dict[str, Any] | None = None) -> ScaffoldPlan:
        """Create a deterministic scaffold plan without calling any model."""
        stack = cls.infer_stack(goal, context)
        factory = {
            "presentation_deck": cls._presentation_deck,
            "fastapi_service": cls._fastapi_service,
            "static_site": cls._static_site,
            "fullstack_fastapi_static": cls._fullstack_fastapi_static,
            "python_package": cls._python_package,
        }[stack]
        return factory(goal)

    @classmethod
    def validate_file_set(cls, files: Iterable[Dict[str, Any]], plan: ScaffoldPlan) -> Dict[str, Any]:
        """Validate parsed/generated files against a scaffold plan."""
        seen = {str(file.get("path", "")).strip() for file in files if file.get("path")}
        empty = [str(file.get("path", "")) for file in files if not str(file.get("content") or file.get("code") or "").strip()]
        missing = [path for path in plan.required_paths() if path not in seen]
        return {
            "passed": not missing and not empty,
            "missing_required_files": missing,
            "empty_files": empty,
            "required_count": len(plan.required_paths()),
            "seen_count": len(seen),
        }

    @classmethod
    def validate_workspace(cls, workspace: str | Path, plan: ScaffoldPlan) -> Dict[str, Any]:
        """Validate that a materialized scaffold exists and has non-empty files."""
        root = Path(workspace)
        missing: List[str] = []
        empty: List[str] = []
        for rel_path in plan.required_paths():
            path = root / rel_path
            if not path.exists():
                missing.append(rel_path)
            elif path.is_file() and path.stat().st_size == 0:
                empty.append(rel_path)
        return {
            "passed": not missing and not empty,
            "missing_required_files": missing,
            "empty_files": empty,
            "workspace": str(root),
        }

    @staticmethod
    def invoke(goal: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Skill-style invocation used by SkillOrchestrator."""
        context = context or {}
        plan = ProductionScaffolder.create_plan(goal, context.get("context", context))
        return {
            "capabilities": [
                "deterministic_project_scaffold",
                "free_first_local_dependencies",
                "validation_gate_checklist",
            ],
            "production_scaffold": plan.to_context(),
            "prompt_block": plan.to_prompt_block(),
        }

    @classmethod
    def _fullstack_fastapi_static(cls, goal: str) -> ScaffoldPlan:
        return ScaffoldPlan(
            stack="fullstack_fastapi_static",
            description=f"Full-stack production app scaffold for: {goal}",
            files=[
                ScaffoldFile("SPEC.md", "Product requirements, roles, data model, user journeys"),
                ScaffoldFile("README.md", "Local setup, architecture, validation checklist"),
                ScaffoldFile(".env.example", "Document local environment variables without secrets"),
                ScaffoldFile("requirements.txt", "FastAPI, uvicorn, pydantic, pytest, httpx"),
                ScaffoldFile("app/main.py", "FastAPI entrypoint, health route, API router registration"),
                ScaffoldFile("app/config.py", "Settings loaded from environment with safe defaults"),
                ScaffoldFile("app/models.py", "Domain data models or SQLAlchemy models"),
                ScaffoldFile("app/schemas.py", "Pydantic request/response schemas"),
                ScaffoldFile("app/api.py", "Versioned REST endpoints and validation"),
                ScaffoldFile("app/services.py", "Business logic separated from routes"),
                ScaffoldFile("static/index.html", "Responsive app shell"),
                ScaffoldFile("static/styles.css", "Production-grade responsive styling"),
                ScaffoldFile("static/app.js", "Frontend state, API calls, graceful error handling"),
                ScaffoldFile("tests/test_app.py", "Health/API smoke tests"),
                ScaffoldFile("Dockerfile", "Local container build using free base images"),
                ScaffoldFile("docker-compose.yml", "Local app service with optional open-source database"),
            ],
            validation_commands=[
                "python -m py_compile app/main.py app/config.py app/models.py app/schemas.py app/api.py app/services.py",
                "pytest -q",
                "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
            ],
            quality_gates=[
                *cls.COMMON_GATES,
                "API routes must return JSON and include /health.",
                "Frontend must call the local API and render loading/error/empty states.",
                "Docker compose must run locally without paid cloud services.",
            ],
            notes=[
                "Use SQLite by default unless the user asks for PostgreSQL.",
                "Keep auth local/dev-safe unless the user explicitly provides a real auth provider.",
            ],
        )

    @classmethod
    def _fastapi_service(cls, goal: str) -> ScaffoldPlan:
        return ScaffoldPlan(
            stack="fastapi_service",
            description=f"REST API service scaffold for: {goal}",
            files=[
                ScaffoldFile("SPEC.md", "API contract, resources, auth assumptions"),
                ScaffoldFile("README.md", "Run, test, and endpoint documentation"),
                ScaffoldFile(".env.example", "Local env variables"),
                ScaffoldFile("requirements.txt", "FastAPI service dependencies"),
                ScaffoldFile("app/main.py", "FastAPI app and health endpoint"),
                ScaffoldFile("app/schemas.py", "Pydantic schemas"),
                ScaffoldFile("app/routes.py", "REST routes"),
                ScaffoldFile("app/services.py", "Business logic"),
                ScaffoldFile("tests/test_api.py", "API smoke tests"),
            ],
            validation_commands=[
                "python -m py_compile app/main.py app/schemas.py app/routes.py app/services.py",
                "pytest -q",
            ],
            quality_gates=[*cls.COMMON_GATES, "Every endpoint must document success and error responses."],
        )

    @classmethod
    def _static_site(cls, goal: str) -> ScaffoldPlan:
        return ScaffoldPlan(
            stack="static_site",
            description=f"Static website scaffold for: {goal}",
            files=[
                ScaffoldFile("SPEC.md", "Audience, sections, content strategy, conversion goals"),
                ScaffoldFile("README.md", "Local preview and customization instructions"),
                ScaffoldFile("index.html", "Semantic accessible HTML"),
                ScaffoldFile("styles.css", "Responsive custom CSS"),
                ScaffoldFile("app.js", "Progressive enhancement only"),
            ],
            validation_commands=["python -m http.server 8000"],
            quality_gates=[*cls.COMMON_GATES, "Page must be accessible, responsive, and not rely on paid CDNs."],
        )

    @classmethod
    def _presentation_deck(cls, goal: str) -> ScaffoldPlan:
        return ScaffoldPlan(
            stack="presentation_deck",
            description=f"Presentation deck scaffold for: {goal}",
            files=[
                ScaffoldFile("SPEC.md", "Audience, objective, storyline, evidence"),
                ScaffoldFile("README.md", "How to present/export the deck"),
                ScaffoldFile("deck.html", "Self-contained HTML slide deck"),
                ScaffoldFile("styles.css", "Presentation theme and print styles"),
                ScaffoldFile("speaker-notes.md", "Slide-by-slide speaker notes"),
            ],
            validation_commands=["python -m http.server 8000"],
            quality_gates=[*cls.COMMON_GATES, "Deck must include speaker notes and a clear narrative arc."],
        )

    @classmethod
    def _python_package(cls, goal: str) -> ScaffoldPlan:
        return ScaffoldPlan(
            stack="python_package",
            description=f"Python project scaffold for: {goal}",
            files=[
                ScaffoldFile("SPEC.md", "Scope, CLI/API contract, edge cases"),
                ScaffoldFile("README.md", "Install, run, and test instructions"),
                ScaffoldFile("pyproject.toml", "Package metadata and dev dependencies"),
                ScaffoldFile("src/main.py", "Application entrypoint"),
                ScaffoldFile("tests/test_main.py", "Smoke tests"),
            ],
            validation_commands=["python -m py_compile src/main.py", "pytest -q"],
            quality_gates=[*cls.COMMON_GATES, "Package must be runnable locally with Python only."],
        )
