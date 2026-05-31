"""
Skill Orchestrator - Coordinates 259+ skills across agent lifecycle
"""

from typing import Any, Dict, List

from neuro.skills.agent_memory import MemoryType, remember
from neuro.skills.agent_memory import get_context as get_memory_context

# Import directly from modules to avoid circular imports
from neuro.skills.automation import SkillAutomation
from neuro.skills.open_design_skills import OpenDesignSkills
from neuro.ultimate.skills_100 import auto_detect_skills

# SKILL_REGISTRY will be set after all imports complete
SKILL_REGISTRY = {}


class SkillOrchestrator:
    """
    Orchestrates all 259+ skills across the agent lifecycle.
    Skills are auto-detected and invoked at appropriate stages.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.active_skills: List[str] = []
        self.skill_results: Dict[str, Any] = {}
        self.ultimate_analysis: Dict[str, Any] = {}
        # Lazy import SKILL_REGISTRY to avoid circular imports
        self._registry = None
        self._enhanced_registry = None


    @property
    def enhanced_registry(self):
        """Lazy load the ultimate registry so core skills and MCP hints are wired in."""
        if self._enhanced_registry is None:
            try:
                from neuro.ultimate.skill_registry import get_enhanced_registry

                self._enhanced_registry = get_enhanced_registry()
            except Exception as exc:
                if self.verbose:
                    print(f"⚠️ Ultimate registry unavailable: {exc}")
                self._enhanced_registry = False
        return self._enhanced_registry or None

    @property
    def skill_registry(self):
        """Lazy load SKILL_REGISTRY to avoid circular imports."""
        if self._registry is None:
            from neuro.skills import SKILL_REGISTRY as _reg
            self._registry = _reg
        return self._registry

    def detect_skills(self, goal: str, context: Dict[str, Any] = None) -> List[str]:
        """Auto-detect which skills to invoke based on goal and context."""
        context = context or {}

        # Use SkillAutomation for keyword-based detection
        trigger_result = SkillAutomation.auto_trigger(goal, context)
        detected = trigger_result.get("detected_skills", [])

        # Also check OpenDesignSkills for specific matches
        open_result = OpenDesignSkills.invoke(goal, context)
        for skill in open_result.get("matched_skills", []):
            if skill["name"] not in detected:
                detected.append(skill["name"])

        if self._needs_production_scaffold(goal):
            for scaffold_skill in ("production_scaffolder", "production_pipeline"):
                if scaffold_skill not in detected:
                    detected.append(scaffold_skill)

        if self._needs_live_web_research(goal):
            if "firecrawl_research" not in detected:
                detected.append("firecrawl_research")

        if self._needs_cinematic_design(goal):
            if "cinematic_design" not in detected:
                detected.append("cinematic_design")

        # Wire in the ultimate registry without changing model/provider selection.
        enhanced_registry = self.enhanced_registry
        if enhanced_registry:
            try:
                self.ultimate_analysis = enhanced_registry.get_skills_for_task(goal, context)
                for skill in self.ultimate_analysis.get("selected_skills", []):
                    if skill["name"] not in detected:
                        detected.append(skill["name"])
                for skill in self.ultimate_analysis.get("matched_3d_skills", []):
                    if skill["name"] not in detected:
                        detected.append(skill["name"])
                for skill in self.ultimate_analysis.get("matched_enterprise_skills", []):
                    if skill["name"] not in detected:
                        detected.append(skill["name"])
            except Exception as exc:
                if self.verbose:
                    print(f"⚠️ Ultimate skill detection error: {exc}")

        self.active_skills = sorted(set(detected))

        if self.verbose and self.active_skills:
            print(f"🎯 Skills detected: {', '.join(self.active_skills)}")

        return self.active_skills

    @staticmethod
    def _needs_production_scaffold(goal: str) -> bool:
        """Return True for build requests that benefit from deterministic scaffolds."""
        goal_lower = goal.lower()
        triggers = [
            "app", "website", "dashboard", "saas", "crm", "cms", "api",
            "full stack", "full-stack", "enterprise", "landing", "presentation",
            "slides", "deck", "admin", "portal", "ecommerce", "e-commerce",
        ]
        return any(trigger in goal_lower for trigger in triggers)

    @staticmethod
    def _needs_live_web_research(goal: str) -> bool:
        """Return True when optional clean web/docs scraping context is useful."""
        goal_lower = goal.lower()
        triggers = [
            "http://", "https://", "scrape", "crawl", "firecrawl", "live docs",
            "official docs", "web research", "research github", "extract website",
            "current docs", "latest docs", "documentation from",
        ]
        return any(trigger in goal_lower for trigger in triggers)

    @staticmethod
    def _needs_cinematic_design(goal: str) -> bool:
        """Return True for premium visual/cinematic UI generation tasks."""
        goal_lower = goal.lower()
        triggers = [
            "cinematic", "premium", "3d effect", "dark theme", "motion graphics",
            "hero section", "gradient", "spotlight", "animation", "web design",
            "landing page", "premium website", "extract from video",
            "build from reference", "visual analysis", "design system",
        ]
        return any(trigger in goal_lower for trigger in triggers)

    def enrich_context(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with skill-specific information."""
        enriched = context.copy()
        skill_hints = []

        skill_analysis = auto_detect_skills(goal)
        selected_auto_skills = skill_analysis.get("selected_skills", [])[:5]
        skill_instructions = []
        for skill in selected_auto_skills:
            name = skill.get("name", "unknown_skill")
            capabilities = skill.get("capabilities", [])[:3]
            capability_text = ", ".join(str(item) for item in capabilities)
            instruction = f"- Use {name}"
            if capability_text:
                instruction += f": {capability_text}"
            if skill.get("description"):
                instruction += f" — {skill['description']}"
            skill_instructions.append(instruction)
            if name not in self.active_skills:
                self.active_skills.append(name)

        if skill_instructions:
            enriched["skill_instructions"] = "\n".join(skill_instructions)
            enriched["auto_detected_skills"] = [skill.get("name") for skill in selected_auto_skills]
            enriched["auto_skill_task_type"] = skill_analysis.get("task_type")
            skill_hints.extend(skill_instructions)

        for skill_name in self.active_skills:
            try:
                # Get skill-specific context
                registry = self.skill_registry
                if skill_name in registry:
                    skill_class = registry[skill_name]
                    if skill_class is None:
                        try:
                            from neuro.skills import _lazy_get_skill

                            skill_class = _lazy_get_skill(skill_name)
                            registry[skill_name] = skill_class
                        except Exception as exc:
                            if self.verbose:
                                print(f"⚠️ Lazy skill {skill_name} unavailable: {exc}")
                            skill_class = None
                    if skill_class:
                        from neuro.skills import invoke_skill_class

                        result = invoke_skill_class(skill_name, skill_class, goal, {"context": context})
                        self.skill_results[skill_name] = result

                        # Add skill-specific hints to context
                        if "capabilities" in result:
                            skill_hints.append(f"[{skill_name}]: {result.get('capabilities', [])[:3]}")

                        if "production_scaffold" in result:
                            enriched["production_scaffold"] = result["production_scaffold"]
                            if result.get("prompt_block"):
                                enriched["production_scaffold_prompt"] = result["prompt_block"]
                                skill_hints.append(result["prompt_block"])

                        if "production_build_plan" in result:
                            enriched["production_build_plan"] = result["production_build_plan"]
                            if result.get("prompt_block"):
                                enriched["production_pipeline_prompt"] = result["prompt_block"]
                                skill_hints.append(result["prompt_block"])

                        if skill_name == "firecrawl_research":
                            if result.get("prompt_block"):
                                enriched["firecrawl_prompt"] = result["prompt_block"]
                                skill_hints.append(result["prompt_block"])
                            if result.get("firecrawl_context"):
                                enriched["firecrawl_context"] = result["firecrawl_context"]
                            enriched["firecrawl_status"] = result.get("status", "unknown")
                            enriched["firecrawl_enabled"] = result.get("enabled", False)

                        if skill_name == "cinematic_design":
                            if result.get("cinematic_prompt"):
                                enriched["cinematic_design_prompt"] = result["cinematic_prompt"]
                                skill_hints.append(result["cinematic_prompt"])
                            if result.get("cinematic_analysis"):
                                enriched["cinematic_analysis"] = result["cinematic_analysis"]
                            if result.get("cinematic_component"):
                                enriched["cinematic_component"] = result["cinematic_component"]

                        # Add MCP endpoint if available
                        if "endpoint" in result:
                            enriched[f"{skill_name}_endpoint"] = result["endpoint"]

                        # Add memory context if available
                        if skill_name in ["agent_memory", "swarmvault"]:
                            mem_context = get_memory_context(goal)
                            if mem_context:
                                enriched["memory_context"] = mem_context

                        # Add browser config if available
                        if skill_name in ["browser_automation", "playwright"]:
                            if "config" in result:
                                enriched["browser_config"] = result["config"]
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Skill {skill_name} error: {e}")

        if self.ultimate_analysis:
            enriched["ultimate_task_analysis"] = self.ultimate_analysis
            enriched["mcp_servers"] = self.ultimate_analysis.get("mcp_servers", [])
            enriched["task_type"] = self.ultimate_analysis.get("task_type")

        if skill_hints:
            enriched["skill_hints"] = "\n".join(skill_hints)
            enriched.setdefault("skill_instructions", enriched["skill_hints"])

        return enriched

    def invoke_skills_for_stage(self, stage: str, data: Any) -> Dict[str, Any]:
        """Invoke relevant skills for a specific execution stage."""
        results = {}

        # Stage-specific skill invocation
        stage_skills = {
            "analysis": ["code-review", "security", "code-simplifier"],
            "implementation": ["github", "git", "docker"],
            "testing": ["qa-changes", "iterate"],
            "deployment": ["docker", "kubernetes", "vercel"],
            "monitoring": ["datadog", "slack-channel-monitor"],
        }

        registry = self.skill_registry
        for skill_name in self.active_skills:
            if skill_name in stage_skills.get(stage, []):
                try:
                    if skill_name in registry:
                        skill_class = registry[skill_name]
                        if skill_class is None:
                            try:
                                from neuro.skills import _lazy_get_skill

                                skill_class = _lazy_get_skill(skill_name)
                                registry[skill_name] = skill_class
                            except Exception as exc:
                                if self.verbose:
                                    print(f"⚠️ Lazy stage skill {skill_name} unavailable: {exc}")
                                skill_class = None
                        if hasattr(skill_class, 'invoke'):
                            result = skill_class.invoke(str(data), {"stage": stage})
                            results[skill_name] = result
                except Exception as exc:
                    if self.verbose:
                        print(f"⚠️ Stage skill {skill_name} error: {exc}")

        return results

    def learn_from_task(self, goal: str, success: bool, context: Dict[str, Any]):
        """Store learning from task completion in agent memory."""
        try:
            summary = f"Task: {goal[:100]}... Success: {success}"
            tags = self.active_skills.copy()
            if success:
                tags.append("success")
            else:
                tags.append("failure")

            remember(
                content=summary,
                memory_type=MemoryType.EPISODIC,
                tags=tags,
                context=context
            )
        except Exception as exc:
            if self.verbose:
                print(f"⚠️ Skill learning error: {exc}")
