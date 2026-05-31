"""Deterministic production build pipeline for free-model app generation.

The pipeline turns a scaffold into staged work packets so the current free models
can generate smaller, verifiable slices instead of one huge fragile response.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from neuro.skills.production_scaffolder import ProductionScaffolder, ScaffoldPlan


@dataclass(frozen=True)
class BuildStage:
    """A deterministic stage in a production app build."""

    name: str
    objective: str
    files: List[str]
    validation: List[str]
    repair_prompt: str


@dataclass(frozen=True)
class ProductionBuildPlan:
    """A complete staged plan for generating and validating an app."""

    scaffold: ScaffoldPlan
    stages: List[BuildStage]
    final_gates: List[str]

    def to_context(self) -> Dict[str, Any]:
        """Return a prompt-friendly dictionary representation."""
        return {
            "stack": self.scaffold.stack,
            "stages": [stage.__dict__ for stage in self.stages],
            "final_gates": self.final_gates,
            "scaffold": self.scaffold.to_context(),
        }

    def to_prompt_block(self) -> str:
        """Render concise staged instructions for the thinking loop."""
        stage_blocks = []
        for index, stage in enumerate(self.stages, 1):
            stage_blocks.append(
                "\n".join(
                    [
                        f"Stage {index}: {stage.name}",
                        f"Objective: {stage.objective}",
                        "Files:",
                        *[f"- {path}" for path in stage.files],
                        "Validation:",
                        *[f"- {command}" for command in stage.validation],
                        f"Repair focus: {stage.repair_prompt}",
                    ]
                )
            )
        gates = "\n".join(f"- {gate}" for gate in self.final_gates)
        return (
            "Production build pipeline (generate in stages; validate after each stage):\n\n"
            + "\n\n".join(stage_blocks)
            + f"\n\nFinal quality gates:\n{gates}"
        )


class ProductionBuildPipeline:
    """Create staged production build plans from deterministic scaffolds."""

    FINAL_GATES = [
        "All required scaffold files exist and are non-empty.",
        "Generated code has a local run path and test path.",
        "No paid/card-required services are required.",
        "No secrets, tokens, or real credentials are hardcoded.",
        "Frontend, backend, docs, and tests match the requested domain.",
    ]

    @classmethod
    def create_plan(cls, goal: str, context: Dict[str, Any] | None = None) -> ProductionBuildPlan:
        """Create a staged build plan for the user's goal."""
        scaffold = ProductionScaffolder.create_plan(goal, context)
        stage_files = cls._group_files(scaffold)
        stages = [
            BuildStage(
                name="spec_and_contract",
                objective="Lock product scope, user roles, data model, and local setup before code.",
                files=stage_files["spec"],
                validation=["Check SPEC.md and README.md are specific to the requested app."],
                repair_prompt="If scope is vague, rewrite SPEC.md with concrete domain entities and workflows.",
            ),
            BuildStage(
                name="backend_and_data",
                objective="Create backend entrypoint, schemas, routes, services, and data model.",
                files=stage_files["backend"],
                validation=[cmd for cmd in scaffold.validation_commands if "py_compile" in cmd] or ["python -m py_compile app/main.py"],
                repair_prompt="Fix imports, route registration, schema mismatches, and missing health/API endpoints.",
            ),
            BuildStage(
                name="frontend_experience",
                objective="Create the UI shell with loading/error/empty states and local API wiring.",
                files=stage_files["frontend"],
                validation=["Open static/index.html locally or serve via python -m http.server when applicable."],
                repair_prompt="Fix broken selectors, missing API calls, poor responsive layout, or generic copy.",
            ),
            BuildStage(
                name="tests_and_deployment",
                objective="Add smoke tests, environment example, and local container/run instructions.",
                files=stage_files["ops"],
                validation=[cmd for cmd in scaffold.validation_commands if "pytest" in cmd] or ["pytest -q"],
                repair_prompt="Fix failing tests, missing env documentation, and local-only deployment instructions.",
            ),
        ]
        return ProductionBuildPlan(scaffold=scaffold, stages=stages, final_gates=cls.FINAL_GATES)

    @classmethod
    def invoke(cls, goal: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Skill-style invocation used by SkillOrchestrator."""
        context = context or {}
        plan = cls.create_plan(goal, context.get("context", context))
        return {
            "capabilities": [
                "stage_by_stage_generation",
                "validation_after_each_stage",
                "targeted_repair_prompts",
                "free_first_build_flow",
            ],
            "production_build_plan": plan.to_context(),
            "prompt_block": plan.to_prompt_block(),
        }

    @classmethod
    def validate_progress(cls, generated_files: Iterable[Dict[str, Any]], plan: ProductionBuildPlan) -> Dict[str, Any]:
        """Report which build stages have all files present and non-empty."""
        files = {
            str(item.get("path", "")): str(item.get("content") or item.get("code") or "")
            for item in generated_files
            if item.get("path")
        }
        stage_results = []
        for stage in plan.stages:
            missing = [path for path in stage.files if path and path not in files]
            empty = [path for path in stage.files if path in files and not files[path].strip()]
            stage_results.append(
                {
                    "stage": stage.name,
                    "passed": not missing and not empty,
                    "missing_files": missing,
                    "empty_files": empty,
                    "repair_prompt": stage.repair_prompt,
                }
            )
        return {
            "passed": all(result["passed"] for result in stage_results),
            "stages": stage_results,
        }

    @staticmethod
    def _group_files(scaffold: ScaffoldPlan) -> Dict[str, List[str]]:
        """Group scaffold files into generation stages."""
        groups = {"spec": [], "backend": [], "frontend": [], "ops": []}
        for path in scaffold.required_paths():
            if path in {"SPEC.md", "README.md"}:
                groups["spec"].append(path)
            elif path.startswith("app/") or path.startswith("src/"):
                groups["backend"].append(path)
            elif path.startswith("static/") or path in {"index.html", "styles.css", "app.js", "deck.html", "speaker-notes.md"}:
                groups["frontend"].append(path)
            else:
                groups["ops"].append(path)
        return groups
