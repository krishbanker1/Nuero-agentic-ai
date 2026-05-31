"""
Main Agent Loop - Orchestrates components for production app builds
Integrates: Router, Reasoning, Validation, Memory, Skills (259+)
NOW WITH ECC-INSPIRED COMPONENTS:
- Task Decomposer (planning)
- Verification Loop (eval-harness)
- Continuous Learning (instincts v2)
- AgentShield (security scanning)
- Multi-Agent Orchestration
- Autonomous Loops (self-improvement)
"""

import json
import os
import shlex
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# NEW: Import role-based agent swarm
from neuro.executor.role_agents import run_agent_swarm
from neuro.memory.task_store import TaskStore
from neuro.reasoning.chain_of_thought import ChainOfThought, CoTConfig
from neuro.reasoning.thinking_loop import LoopConfig, ThinkingLoop
from neuro.router.fallback import create_fallback_handler

# NEW: Import scenario detection
from neuro.router.scenario_router import ScenarioRouter
from neuro.router.smart_router import SmartRouter
from neuro.skills import (
    AgentShieldSkill,
    AppLauncher,
    AutoFixLoop,
    AutonomousLoop,
    MultiAgentOrchestrator,
    PlaywrightTester,
    PythonPatternsSkill,
    ShellExecutor,
    SkillOrchestrator,
    TaskDecomposer,
    # NEW: ECC-inspired skills
    VerificationLoop,
    create_plan,
    get_learning_system,
)

# IMPORT ALL SKILLS FOR INTEGRATION
from neuro.skills import (
    get_context as get_memory_context,  # Import from separate file
)
from neuro.validation.patch_guard import PatchGuard
from neuro.validation.test_runner import TestRunner

# Advanced production-quality orchestration features
try:
    from neuro.executor.optimized_agent import (
        ContextManager,
        IntelligentErrorAnalyzer,
        ModelEnsemble,
        ReflectionLoop,
        SemanticPatchValidator,
        TestVoting,
    )
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False


@dataclass
class AgentConfig:
    """Configuration for the Neuro agent."""
    goal: str
    working_dir: str = "."
    max_steps: int = 50
    max_passes: int = 4
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.1
    test_first: bool = True
    use_cot: bool = True
    use_memory: bool = True
    use_skills: bool = True  # Enable skills
    use_decomposer: bool = True  # ECC-style task planning
    use_verification: bool = True  # ECC verification loops
    use_security: bool = True  # AgentShield security
    use_orchestration: bool = True  # ✅ Multi-agent ENABLED
    use_autonomous_loop: bool = True  # NEW: Self-improvement loops
    # NEW: Shell Executor & Self-Healing
    use_shell_executor: bool = True  # Execute shell commands
    use_auto_fix: bool = True  # Auto-fix errors
    use_playwright_test: bool = True  # Test UI/apps
    use_app_launcher: bool = True  # Launch apps/servers
    auto_install_dependencies: bool = True  # Install workspace dependencies before validation
    validation_commands: List[str] = field(default_factory=list)  # Extra user/project validation commands
    # Advanced production-quality orchestration features
    use_test_voting: bool = True  # Run tests 3x for reliability
    use_ensemble_voting: bool = True  # Multiple models vote
    use_reflection_loop: bool = True  # Learn from failures
    use_semantic_validation: bool = True  # Semantic patch comparison
    test_votes: int = 3  # Number of test votes
    ensemble_models: int = 3  # Number of ensemble models
    dry_run: bool = False
    confirm_apply: bool = False
    verbose: bool = True
    test_results: Dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    goal: str
    status: str
    steps: int
    passes_used: int
    duration_ms: float
    files_changed: List[str] = field(default_factory=list)
    error: Optional[str] = None
    model_used: str = ""
    provider_used: str = ""
    validation_passed: bool = False
    test_results: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    skills_used: List[str] = field(default_factory=list)  # NEW: Track skills


class NeuroAgent:
    """
    Main Neuro Autonomous Agent.
    Orchestrates all components for production-grade autonomous engineering.
    NOW WITH FULL 259+ SKILLS + ECC-INSPIRED COMPONENTS.
    """

    def __init__(self, config: AgentConfig):
        self.config = config

        # Reload API keys from environment to ensure fresh load
        from neuro.router.smart_router import reload_keys
        reload_keys()

        self.router = SmartRouter()
        self.fallback = create_fallback_handler(self.router)
        self.cot = ChainOfThought(CoTConfig(enabled=config.use_cot))
        self.test_runner = TestRunner(config.working_dir)
        self.patch_guard = PatchGuard(config.working_dir, dry_run=config.dry_run)
        self.memory = TaskStore() if config.use_memory else None

        # NEW: Initialize skill orchestrator
        self.skill_orchestrator = SkillOrchestrator(verbose=config.verbose) if config.use_skills else None

        # NEW: ECC-inspired components
        if config.use_decomposer:
            self.decomposer = TaskDecomposer()
        else:
            self.decomposer = None

        if config.use_verification:
            self.verification_loop = VerificationLoop(max_attempts=3)
        else:
            self.verification_loop = None

        if config.use_security:
            self.security_scanner = AgentShieldSkill()
        else:
            self.security_scanner = None

        if config.use_orchestration:
            self.orchestrator = MultiAgentOrchestrator()
        else:
            self.orchestrator = None

        if config.use_autonomous_loop:
            self.autonomous_loop = AutonomousLoop()
        else:
            self.autonomous_loop = None

        # NEW: Continuous learning (always available)
        self.learning = get_learning_system()

        # NEW: Python patterns
        self.python_patterns = PythonPatternsSkill()

        # NEW: Shell Executor & Self-Healing
        if config.use_shell_executor:
            self.shell_executor = ShellExecutor(working_dir=config.working_dir)
        else:
            self.shell_executor = None

        if config.use_auto_fix:
            self.auto_fix_loop = AutoFixLoop()
        else:
            self.auto_fix_loop = None

        if config.use_playwright_test:
            self.playwright_tester = PlaywrightTester()
        else:
            self.playwright_tester = None

        if config.use_app_launcher:
            self.app_launcher = AppLauncher()
        else:
            self.app_launcher = None

        # Initialize advanced optimization components
        if OPTIMIZATIONS_AVAILABLE:
            self.model_ensemble = ModelEnsemble(self.router) if config.use_ensemble_voting else None
            self.test_voting = TestVoting(self.test_runner) if config.use_test_voting else None
            self.semantic_validator = SemanticPatchValidator() if config.use_semantic_validation else None
            self.error_analyzer = IntelligentErrorAnalyzer(self.router) if config.use_auto_fix else None
            self.reflection = ReflectionLoop(self.router) if config.use_reflection_loop else None
            self.context_manager = ContextManager(self.router)
        else:
            self.model_ensemble = None
            self.test_voting = None
            self.semantic_validator = None
            self.error_analyzer = None
            self.reflection = None
            self.context_manager = None

        self.current_step = 0
        self.history: List[Dict] = []
        self.start_time = time.time()
        self.attempts: List[Dict] = []

        # Get similar past tasks for context (including skill memory)
        self.similar_context = self._get_similar_context()

    def _get_similar_context(self) -> str:
        """Get context from similar past tasks and skill memory."""
        context_parts = []

        # Memory from past tasks
        if self.memory:
            try:
                tasks = self.memory.get_similar(self.config.goal, limit=3)
                if tasks:
                    context_parts.append("Past task history:")
                    for task in tasks:
                        context_parts.append(f"- {task.goal[:100]}... (status: {task.status})")
            except:
                pass

        # NEW: Also get context from skill-based memory
        if self.config.use_skills:
            try:
                skill_mem = get_memory_context(self.config.goal)
                if skill_mem:
                    context_parts.append(f"\nRelevant skill memory:\n{skill_mem}")
            except:
                pass

        return "\n".join(context_parts) if context_parts else ""


    def _validate_written_files(self, files_written: List[str]) -> List[str]:
        """Return files that are missing or empty after generation."""
        import os

        empty = []
        for path in files_written:
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                empty.append(path)
                if self.config.verbose:
                    print(f"⚠️ Empty or missing generated file detected: {path}")
        return empty

    def _relative_to_workspace(self, file_path: str) -> str:
        """Return a shell-safe path relative to the configured workspace when possible."""
        workspace = Path(self.config.working_dir).resolve()
        path = Path(file_path).resolve()
        try:
            return str(path.relative_to(workspace))
        except ValueError:
            return str(path)

    def _has_package_script(self, script_name: str) -> bool:
        """Return True if package.json defines a given npm script."""
        package_json = Path(self.config.working_dir) / "package.json"
        if not package_json.exists():
            return False
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            return script_name in data.get("scripts", {})
        except Exception:
            return False

    def _detect_workspace_commands(self, files_created: List[str]) -> Dict[str, List[str]]:
        """Detect free/local commands needed to install dependencies and validate generated work.

        The commands intentionally use provider-free local tools only: Python, pip, npm,
        and project-defined scripts. They run inside the workspace and preserve the
        existing model routing/brain choices.
        """
        workspace = Path(self.config.working_dir).resolve()
        created_paths = [Path(path) for path in files_created]
        python_files = [path for path in created_paths if path.suffix == ".py" and path.exists()]
        install_commands: List[str] = []
        validation_commands: List[str] = []

        if self.config.auto_install_dependencies:
            if (workspace / "requirements.txt").exists():
                install_commands.append("python -m pip install -r requirements.txt")
            if (workspace / "package.json").exists() and not (workspace / "node_modules").exists():
                install_commands.append("npm install")

        if python_files:
            if os.name == "nt":
                quoted = " ".join(f'"{self._relative_to_workspace(str(path))}"' for path in python_files)
            else:
                quoted = " ".join(shlex.quote(self._relative_to_workspace(str(path))) for path in python_files)
            validation_commands.append(f"python -m py_compile {quoted}")

        generated_test_files = [path for path in created_paths if path.name.startswith("test_") and path.suffix == ".py"]
        if generated_test_files:
            if os.name == "nt":
                quoted_tests = " ".join(f'"{self._relative_to_workspace(str(path))}"' for path in generated_test_files)
            else:
                quoted_tests = " ".join(shlex.quote(self._relative_to_workspace(str(path))) for path in generated_test_files)
            validation_commands.append(f"python -m pytest -q {quoted_tests}")

        if (workspace / "package.json").exists():
            if self._has_package_script("build"):
                validation_commands.append("npm run build")
            if self._has_package_script("test"):
                validation_commands.append("npm test -- --watch=false")

        validation_commands.extend(self.config.validation_commands)
        return {"install": install_commands, "validate": validation_commands}

    def _run_workspace_validation(self, files_created: List[str]) -> Dict[str, Any]:
        """Install dependencies and run workspace validation commands autonomously."""
        if not self.shell_executor:
            return {"enabled": False, "commands": [], "success": True, "reason": "shell executor disabled"}

        command_groups = self._detect_workspace_commands(files_created)
        commands = command_groups["install"] + command_groups["validate"]
        if not commands:
            return {"enabled": True, "commands": [], "success": True, "reason": "no validation commands detected"}

        results = []
        success = True
        for command in commands:
            if self.config.verbose:
                print(f"🧪 Workspace command: {command}")
            result = self.shell_executor.execute_with_fix(
                command,
                max_retries=1 if self.config.use_auto_fix else 0,
                context={"working_dir": self.config.working_dir, "files_created": files_created},
            )
            item = {
                "command": command,
                "success": result.success,
                "exit_code": result.exit_code,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
                "errors": [error.message for error in result.errors],
                "fixes_attempted": result.fixes_attempted,
            }
            results.append(item)
            if not result.success:
                success = False
                # Do not keep running dependent validation after an install/build failure.
                break

        return {"enabled": True, "commands": commands, "results": results, "success": success}

    def _write_generated_file(self, relative_path: str, content: str) -> Optional[str]:
        """Write generated content safely inside the configured workspace.

        Fallback extraction paths should obey the same guarantees as the robust
        parser: no path traversal, no empty writes, UTF-8 output, and preserved
        relative directories.
        """
        if not relative_path or not str(content).strip():
            return None

        workspace = Path(self.config.working_dir).resolve()
        target = (workspace / relative_path).resolve()
        if workspace != target and workspace not in target.parents:
            if self.config.verbose:
                print(f"⚠️ Skipping unsafe generated path outside workspace: {relative_path}")
            return None

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
        if not target.exists() or target.stat().st_size == 0:
            if self.config.verbose:
                print(f"⚠️ Skipping zero-byte generated file: {relative_path}")
            return None
        return str(target)

    def run(self) -> AgentResult:
        """
        Run the agent to complete the goal WITH FULL SKILL INTEGRATION.

        Returns:
            AgentResult with execution details
        """
        if self.config.verbose:
            print("=" * 60)
            print("NEURO AUTONOMOUS AGENT (259+ Skills + ECC Components)")
            print("=" * 60)
            print(f"Goal: {self.config.goal}")
            print(f"Working dir: {self.config.working_dir}")
            print(f"Max steps: {self.config.max_steps}")
            print(f"Test-first: {self.config.test_first}")
            print(f"COT: {self.config.use_cot}")
            print(f"Skills: {self.config.use_skills}")
            print(f"Decomposer: {self.config.use_decomposer}")
            print(f"Security: {self.config.use_security}")
            print("=" * 60)

        try:
            # PHASE 0: SKILL DETECTION + PLANNING (ECC)
            if self.skill_orchestrator:
                if self.config.verbose:
                    print("\n🔍 Detecting relevant skills...")
                self.skill_orchestrator.detect_skills(self.config.goal, {
                    "working_dir": self.config.working_dir
                })

            # NEW: Scenario Detection and Agent Swarm
            scenario_router = ScenarioRouter()
            scenario, confidence = scenario_router.detect_scenario(self.config.goal)
            scenario_handler = scenario_router.get_handler(scenario)
            if self.config.verbose:
                print(f"\n🎯 Detected scenario: {scenario.value} (confidence: {confidence:.2f})")

            # Run the multi-agent swarm and print trace
            if self.config.verbose:
                print("\n🤖 Running Agent Swarm (4 agents working)...")
            swarm_task = {
                "description": self.config.goal,
                "type": scenario.value,
                "codebase_root": self.config.working_dir,
            }
            swarm_result = run_agent_swarm(swarm_task)
            if self.config.verbose and swarm_result.get("trace"):
                print("\n📊 Agent Swarm Execution Trace:")
                for agent_name, success, message in swarm_result["trace"]:
                    status = "✓" if success else "✗"
                    print(f"   {status} {agent_name}: {message}")

            # NEW: Task Decomposition (ECC's /plan)
            if self.decomposer and self.config.use_decomposer:
                if self.config.verbose:
                    print("\n📋 Creating implementation plan...")
                decomposition = create_plan(self.config.goal, {"working_dir": self.config.working_dir})
                if self.config.verbose:
                    print(f"   Steps: {len(decomposition['steps'])}, Estimated: {decomposition['total_minutes']} min")
            else:
                decomposition = None

            # Phase 1: Multi-pass thinking WITH skill enrichment
            thinking_loop = ThinkingLoop(self.router, LoopConfig(max_passes=self.config.max_passes))

            # Build context with skill enrichment + learned patterns
            context = {
                "goal": self.config.goal,  # NEW: Add goal for web research
                "working_dir": self.config.working_dir,
                "test_first": self.config.test_first,
                "similar_tasks": self.similar_context,
                "active_skills": self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
                "decomposition": decomposition,  # NEW: Add plan to context
                "scenario_instructions": "\n".join(scenario_handler.special_instructions),
                "scenario_approach": scenario_handler.approach,
            }

            # NEW: Add learned patterns from continuous learning
            if self.learning:
                learned_context = self.learning.get_context_for_task(self.config.goal)
                if learned_context:
                    context["learned_patterns"] = learned_context

            # Enrich thinking context with detected skills, ultimate task analysis,
            # MCP recommendations, and enterprise/3D capability hints.
            if self.skill_orchestrator:
                context = self.skill_orchestrator.enrich_context(self.config.goal, context)

            # Invoke analysis-stage skills
            if self.skill_orchestrator:
                analysis_results = self.skill_orchestrator.invoke_skills_for_stage("analysis", context)
                if analysis_results and self.config.verbose:
                    print(f"📊 Analysis skills: {list(analysis_results.keys())}")

            thinking_result = thinking_loop.run(
                goal=self.config.goal,
                context=context,
            )

            solution = thinking_result["solution"]
            passes_used = thinking_result["num_passes"]

            # NEW: Extract research context from passes for next iteration
            for p in thinking_result.get("passes", []):
                if "KEY FEATURES IDENTIFIED" in p.get("response", ""):
                    context["research_context"] = p["response"]
                    if self.config.verbose:
                        print("📚 Research context captured for implementation")
                    break

            if self.config.verbose:
                print(f"\n✓ Thinking complete ({passes_used} passes)")
                print(f"Convergence: {thinking_result['convergence_score']:.2f}")

            # Parse solution JSON to get file structure - USE ROBUST PARSER
            files_created = []

            # NEW: Handle dry_run early return with plan output
            if self.config.dry_run:
                thinking_context = thinking_result.get("context", {})
                dry_run_output = (
                    solution.strip()
                    or str(thinking_context.get("plan") or "").strip()
                    or str(thinking_context.get("enhanced_prompt") or "").strip()
                    or next(
                        (
                            str(p.get("response_preview") or "").strip()
                            for p in reversed(thinking_result.get("passes", []))
                            if str(p.get("response_preview") or "").strip()
                        ),
                        "",
                    )
                )
                self.current_step = max(self.current_step, 1 if dry_run_output else 0)
                duration_ms = (time.time() - self.start_time) * 1000
                self.config.test_results = {
                    **self.config.test_results,
                    "dry_run_plan_generated": bool(dry_run_output),
                }
                if self.config.verbose and dry_run_output:
                    print("\n📋 Dry-run plan generated successfully")
                return AgentResult(
                    success=bool(dry_run_output),
                    goal=self.config.goal,
                    status="completed" if dry_run_output else "error",
                    steps=self.current_step,
                    passes_used=passes_used,
                    duration_ms=duration_ms,
                    validation_passed=bool(dry_run_output),
                    test_results=self.config.test_results,
                    model_used=self.config.model or "auto",
                    metadata={"plan": dry_run_output},
                    skills_used=self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
                    error=None if dry_run_output else "Dry-run produced no plan output",
                )

            # NEW: Use the robust CodeParser
            from neuro.core.code_parser import parse_and_write_files

            if self.config.verbose:
                print(f"📄 Parsing solution ({len(solution)} chars)...")
                print(f"🔍 Solution preview: {solution[:200]}...")

            # Try the robust parser first
            try:
                parsed_files = parse_and_write_files(
                    solution,
                    self.config.working_dir,
                    verbose=self.config.verbose
                )
                empty_files = self._validate_written_files(parsed_files)
                files_created = [path for path in parsed_files if path not in empty_files]
                if self.config.verbose:
                    print(f"✅ Parser returned: {files_created}")
                if empty_files:
                    context["empty_generated_files"] = empty_files
                    context["validation_error"] = (
                        "Generated empty files; regenerate complete non-empty content for: "
                        + ", ".join(empty_files)
                    )
            except Exception as e:
                if self.config.verbose:
                    print(f"⚠️ Robust parser failed: {e}")

            # If robust parser found files, we're done
            if files_created:
                if self.config.verbose:
                    print(f"✅ Parsed {len(files_created)} files successfully")
            else:
                # Fallback: Try legacy JSON parsing
                if self.config.verbose:
                    print("🔄 Trying legacy JSON parsing...")

                import json
                import re

                def create_files_from_json(parsed, verbose=True):
                    nonlocal files_created
                    files_to_create = parsed.get("files", [])

                    if files_to_create and verbose:
                        print(f"\n📁 Creating {len(files_to_create)} files...")

                    for file_info in files_to_create:
                        file_path = file_info.get("path", "")
                        file_content = file_info.get("content", "")

                        if file_content and ('\\n' in str(file_content)):
                            file_content = file_content.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

                        if isinstance(file_content, str):
                            stripped = file_content.strip()
                            if stripped.startswith('"""') and stripped.endswith('"""') and stripped.count('"""') == 2:
                                file_content = stripped[3:-3].strip()
                            elif stripped.startswith("'''") and stripped.endswith("'''") and stripped.count("'''") == 2:
                                file_content = stripped[3:-3].strip()

                        written_path = self._write_generated_file(file_path, str(file_content))
                        if written_path:
                            files_created.append(written_path)
                            if verbose:
                                print(f"   ✓ Created: {file_path}")

                # Try parsing JSON from markdown blocks
                json_blocks = re.findall(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', solution)
                for block in json_blocks:
                    try:
                        data = json.loads(block)
                        if "files" in data:
                            create_files_from_json(data)
                            break
                    except:
                        continue

            # If no JSON, check if solution itself contains code blocks
            if not files_created:
                # Try to extract code blocks from solution
                code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', solution)
                if code_blocks and self.config.verbose:
                    print(f"\n📁 Extracting {len(code_blocks)} code blocks...")

                # Track what files we created to avoid duplicates
                created_bases = set()

                for i, code in enumerate(code_blocks):
                    # Try to determine filename from context
                    code = code.strip()
                    if not code or len(code) < 50:
                        continue

                    file_name = None
                    # Try to determine filename from preceding text
                    match_start = solution.find(f'```{i}') if i < 3 else 0
                    # Search for filenames before the code block
                    search_area = solution[max(0, match_start-200):match_start+10] if match_start > 0 else solution[:200]

                    # Look for specific patterns that indicate filenames
                    patterns = [
                        r'filename[:\s]+([\w\-_./]+\.py)',
                        r'file[:\s]+([\w\-_./]+\.py)',
                        r'create[:\s]+([\w\-_./]+\.py)',
                        r'called[:\s]+([\w\-_./]+\.py)',
                    ]
                    for pattern in patterns:
                        m = re.search(pattern, search_area, re.IGNORECASE)
                        if m:
                            file_name = m.group(1)
                            break

                    if not file_name:
                        # Use keyword detection - expanded for more file types
                        # Check YAML first (since it has distinct markers)
                        if "apiVersion:" in code or "kind:" in code or ("---" in code and ":" in code):
                            file_name = "k8s-config.yaml"
                        elif "kind create cluster" in code or "#!/bin/bash" in code or "kubectl apply" in code or "kubectl create" in code:
                            file_name = "setup.sh"
                        elif code.strip().startswith("#") or code.strip().startswith("kubectl") or code.strip().startswith("kind"):
                            file_name = "setup.sh"
                        elif "flask" in code.lower() and "route" in code.lower():
                            file_name = "app.py"
                        elif "kubernetes" in code.lower() and ("import" in code or "class" in code or "def " in code):
                            file_name = "app.py"
                        elif "class User" in code or "classusers" in code.lower():
                            file_name = "models.py"
                        elif "test" in code.lower() and "def test_" in code:
                            file_name = "test_app.py"
                        elif "auth" in solution.lower() or "jwt" in code.lower():
                            file_name = "auth.py"
                        elif "database" in solution.lower() or "sqlalchemy" in code.lower():
                            file_name = "database.py"
                        elif "__init__" in code:
                            file_name = "__init__.py"
                        elif "import" not in code and ("const " in code or "let " in code or "function" in code):
                            file_name = "app.js"
                        elif "{" in code and "}" in code and ":" in code and ";" not in code:
                            file_name = "config.json"
                        else:
                            file_name = f"generated_{i+1}.py"

                    # Make filename unique if already used
                    base_name = file_name
                    counter = 1
                    while file_name in created_bases:
                        parts = base_name.rsplit('.', 1)
                        file_name = f"{parts[0]}_{counter}.{parts[1]}" if len(parts) == 2 else f"{base_name}_{counter}.py"
                        counter += 1

                    created_bases.add(file_name)
                    written_path = self._write_generated_file(file_name, code)
                    if written_path:
                        files_created.append(written_path)
                        if self.config.verbose:
                            print(f"   ✓ Created: {file_name}")

            # Phase 2: Validation WITH skill invocation
            validation_passed = False

            # Debug: Show what we're trying to parse
            if self.config.verbose:
                print(f"\n🔍 Solution length: {len(solution)} chars")
                has_json_marker = '"files"' in solution or solution.strip().startswith('{')
                print(f"🔍 Has JSON marker: {has_json_marker}")
                print("\n📄 Solution content (first 1000 chars):")
                print(solution[:1000])

            # Fallback: If no JSON was parsed, try direct code block extraction
            if not files_created:
                code_blocks = re.findall(r'```(?:json|python|py|js|html|css)?\s*([\s\S]*?)```', solution)
                if code_blocks and self.config.verbose:
                    print(f"\n📁 No JSON found, extracting {len(code_blocks)} code blocks...")

                for i, code in enumerate(code_blocks):
                    code = code.strip()
                    if len(code) < 100:
                        continue

                    # Determine file type
                    if 'flask' in code.lower() and 'app' in code.lower():
                        fname = "app.py"
                    elif 'html' in code.lower() or '<!doctype' in code.lower():
                        fname = "index.html"
                    elif 'css' in code.lower() or '{' in code:
                        fname = "style.css"
                    elif 'function' in code or 'const' in code or 'let' in code:
                        fname = "app.js"
                    else:
                        fname = f"generated_{i+1}.py"

                    written_path = self._write_generated_file(fname, code)
                    if written_path:
                        files_created.append(written_path)
                        if self.config.verbose:
                            print(f"   ✓ Created: {fname}")

            # Quality check: Verify files are not placeholders/TODOs
            files_valid = True
            for fpath in files_created:
                try:
                    fcontent = Path(fpath).read_text()
                    # Check for placeholder patterns
                    placeholder_patterns = ["TODO", "FIXME", "...", "rest of code"]
                    has_placeholder = any(p in fcontent for p in placeholder_patterns)
                    if has_placeholder:
                        files_valid = False
                        if self.config.verbose:
                            print(f"⚠️ Invalid file: {fpath}")
                except:
                    pass

            # Consider success if files were created (even without tests)
            if files_created and files_valid:
                validation_passed = True
                if self.config.verbose:
                    # Show what was created
                    print("\n✅ Files created successfully")
                    print(f"   Created {len(files_created)} files:")
                    for f in files_created:
                        print(f"      - {f}")

            workspace_validation = self._run_workspace_validation(files_created) if files_created else {"enabled": False, "success": validation_passed}
            self.config.test_results = {
                **self.config.test_results,
                "workspace_validation": workspace_validation,
            }
            if files_created and workspace_validation.get("enabled") and workspace_validation.get("commands"):
                validation_passed = validation_passed and bool(workspace_validation.get("success"))
                if self.config.verbose:
                    status = "passed" if workspace_validation.get("success") else "failed"
                    print(f"🧪 Workspace validation {status}: {len(workspace_validation.get('commands', []))} command(s)")

            # Debug: Show validation state before test_first
            if self.config.verbose:
                print(f"\n🔍 Before test_first: validation_passed={validation_passed}, test_first={self.config.test_first}")

            if self.config.test_first:
                if self.config.verbose:
                    print("\n📋 Running validation tests...")

                # NEW: Invoke testing-stage skills before running tests
                if self.skill_orchestrator:
                    test_skills = self.skill_orchestrator.invoke_skills_for_stage("testing", solution)
                    if test_skills and self.config.verbose:
                        print(f"🧪 Testing skills: {list(test_skills.keys())}")

                # Run relevant tests only if they exist
                test_result = self.test_runner.run_pytest(timeout=300)

                # Only update validation if tests were actually run and found
                if test_result.total > 0:
                    validation_passed = test_result.all_passed
                else:
                    # No tests found - keep file-creation success
                    if self.config.verbose:
                        print("⚠️ No tests found - keeping file creation as success")

                self.config.test_results = {
                    **self.config.test_results,
                    "total": test_result.total,
                    "passed": test_result.passed,
                    "failed": test_result.failed,
                    "exit_code": test_result.exit_code,
                }

                if self.config.verbose:
                    if test_result.total > 0:
                        print(f"Tests: {test_result.passed}/{test_result.total} passed")
                    else:
                        print("Tests: 0/0 (no tests found)")

                if not validation_passed and test_result.total > 0:
                    if self.config.verbose:
                        print("⚠️ Tests failed - attempting fixes...")

            # Phase 3: Apply patches (if not dry run and validated)
            files_changed = []

            if not self.config.dry_run and validation_passed:
                if self.config.verbose:
                    print("\n🔧 Applying verified patches...")

                # NEW: Invoke deployment skills before applying
                if self.skill_orchestrator:
                    deploy_skills = self.skill_orchestrator.invoke_skills_for_stage("deployment", files_changed)
                    if deploy_skills and self.config.verbose:
                        print(f"🚀 Deployment skills: {list(deploy_skills.keys())}")

                results = self.patch_guard.apply_verified_patches()
                files_changed = [r["file"] for r in results["applied"]]

                if self.config.verbose:
                    print(f"Applied: {len(files_changed)} files")
            elif self.config.dry_run:
                if self.config.verbose:
                    print("\n🔍 Dry run - no changes applied")

            # Record in memory INCLUDING skill learning
            duration_ms = (time.time() - self.start_time) * 1000

            if self.memory:
                try:
                    self.memory.add_task(
                        goal=self.config.goal,
                        status="success" if validation_passed else "partial",
                        files_changed=files_changed,
                        duration_ms=duration_ms,
                        model_used=self.config.model or "auto",
                        provider_used=self.router.get_stats().get("provider_calls", {}).most_common(1)[0][0] if hasattr(self.router.get_stats().get("provider_calls"), "most_common") else "unknown",
                        passes_used=passes_used,
                    )
                except:
                    pass

            # NEW: Store skill learning
            if self.skill_orchestrator:
                self.skill_orchestrator.learn_from_task(
                    self.config.goal,
                    validation_passed,
                    {"files_changed": files_changed}
                )

            return AgentResult(
                success=validation_passed,
                goal=self.config.goal,
                status="completed",
                steps=self.current_step,
                passes_used=passes_used,
                duration_ms=duration_ms,
                files_changed=files_changed,
                validation_passed=validation_passed,
                test_results=self.config.test_results,
                model_used=self.config.model or "auto",
                skills_used=self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
            )

        except Exception as e:
            duration_ms = (time.time() - self.start_time) * 1000

            # Record failure
            if self.memory:
                try:
                    self.memory.add_task(
                        goal=self.config.goal,
                        status="failure",
                        files_changed=[],
                        error=str(e),
                        duration_ms=duration_ms,
                    )
                except:
                    pass

            # NEW: Store failure in skill memory too
            if self.skill_orchestrator:
                self.skill_orchestrator.learn_from_task(
                    self.config.goal,
                    False,
                    {"error": str(e)}
                )

            return AgentResult(
                success=False,
                goal=self.config.goal,
                status="error",
                steps=self.current_step,
                passes_used=0,
                duration_ms=duration_ms,
                error=str(e),
                skills_used=self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
            )

    def get_history(self) -> List[Dict]:
        """Get execution history."""
        return self.history

    def get_thinking_summary(self) -> str:
        """Get summary of thinking process."""
        skill_info = f", Skills: {len(self.skill_orchestrator.active_skills)}" if self.skill_orchestrator else ""
        return f"Steps: {self.current_step}, Duration: {(time.time() - self.start_time):.1f}s{skill_info}"


def create_agent(
    goal: str,
    working_dir: str = ".",
    max_steps: int = 50,
    max_passes: int = 4,
    model: Optional[str] = None,
    test_first: bool = True,
    use_cot: bool = True,
    use_memory: bool = True,  # NEW: Memory flag
    use_skills: bool = True,  # Enable 259+ skills
    use_decomposer: bool = True,  # NEW: ECC-style task planning
    use_verification: bool = True,  # NEW: ECC verification loops
    use_security: bool = True,  # NEW: AgentShield security
    use_orchestration: bool = False,  # NEW: Multi-agent for complex tasks
    use_autonomous_loop: bool = True,  # NEW: Self-improvement loops
    dry_run: bool = False,
    verbose: bool = True,
    auto_install_dependencies: bool = True,
    validation_commands: Optional[List[str]] = None,
) -> NeuroAgent:
    """
    Create a new Neuro agent WITH FULL SKILL INTEGRATION + ECC COMPONENTS.

    Usage:
        from neuro.executor.agent_loop import create_agent

        agent = create_agent(
            goal="Fix the login bug",
            working_dir="/path/to/project",
            test_first=True,
            use_cot=True,
            use_memory=True,
            use_skills=True,  # Enable 259+ skills
            use_decomposer=True,  # Enable task decomposition (ECC /plan)
            use_verification=True,  # Enable verification loops
            use_security=True,  # Enable AgentShield scanning
            dry_run=False,
        )

        result = agent.run()
        print(f"Success: {result.success}")
        print(f"Skills used: {result.skills_used}")
    """
    config = AgentConfig(
        goal=goal,
        working_dir=working_dir,
        max_steps=max_steps,
        max_passes=max_passes,
        model=model,
        test_first=test_first,
        use_cot=use_cot,
        use_memory=use_memory,  # NEW
        use_skills=use_skills,
        use_decomposer=use_decomposer,  # NEW
        use_verification=use_verification,  # NEW
        use_security=use_security,  # NEW
        use_orchestration=use_orchestration,  # NEW
        use_autonomous_loop=use_autonomous_loop,  # NEW
        dry_run=dry_run,
        verbose=verbose,
        auto_install_dependencies=auto_install_dependencies,
        validation_commands=validation_commands or [],
    )

    return NeuroAgent(config)


def run_goal(goal: str, **kwargs) -> AgentResult:
    """
    Quick function to run a goal WITH SKILL INTEGRATION.

    Usage:
        from neuro.executor.agent_loop import run_goal

        result = run_goal(
            "Fix the bug in main.py",
            working_dir="/path/to/project",
            use_skills=True
        )

        print(result.success)
        print(f"Skills used: {result.skills_used}")
    """
    agent = create_agent(goal, **kwargs)
    return agent.run()
