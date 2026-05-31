from neuro.reasoning.thinking_loop import LoopConfig, PassType, ThinkingLoop
from neuro.skills import SKILL_REGISTRY
from neuro.skills.cinematic_design import CinematicDesign
from neuro.skills.skill_orchestrator import SkillOrchestrator


def test_cinematic_description_derives_premium_motion_patterns():
    design = CinematicDesign()

    analysis = design.analyze_description("dark premium 3d hero section with dynamic motion graphics and spotlight")

    assert analysis["brightness_level"] == "dark"
    assert analysis["depth_perception"] == "3d"
    assert analysis["motion_level"] == "heavy"
    assert "dark_cinematic" in analysis["patterns_needed"]
    assert "3d_depth" in analysis["patterns_needed"]
    assert "motion" in analysis["patterns_needed"]


def test_cinematic_component_generation_derives_css_and_react():
    design = CinematicDesign()
    result = design.build_from_input(
        "premium dark cinematic 3d product landing page with smooth animation",
        {"title": "Neuro", "subtitle": "Build anything", "cta": "Start"},
    )

    assert result["component_name"] == "CinematicHero"
    assert "3d_depth" in result["patterns_used"]
    assert "dark_cinematic" in result["patterns_used"]
    assert "gradient-depth" in result["css"]
    assert "CinematicHero" in result["jsx"]
    assert result["analysis_metadata"]["depth_perception"] in {"2.5d", "3d"}
    assert result["technology_stack"]["animation_library"] in {"gsap", "framer_motion"}
    assert result["technology_stack"]["3d_library"] in {"threejs", "babylonjs", "css_3d"}
    assert "library_code" in result
    assert result["packages"]


def test_cinematic_detects_full_library_stack_from_analysis():
    design = CinematicDesign()
    analysis = design.analyze_description("dark premium 3d animated product hero with dynamic motion and spotlight")
    component = design.generate_complete_component(analysis, {"title": "X", "subtitle": "Y", "cta": "Go"})

    assert component["technology_stack"]["animation_library"] == "gsap"
    assert component["technology_stack"]["text_animation"] == "split_type"
    assert "animation_code" in component["library_code"]
    assert "text_code" in component["library_code"]
    assert "gsap" in component["packages"]


def test_cinematic_skill_registry_and_orchestrator_prompt():
    assert SKILL_REGISTRY["cinematic_design"] is CinematicDesign

    orchestrator = SkillOrchestrator(verbose=False)
    skills = orchestrator.detect_skills("Build a premium cinematic landing page with 3d hero animation", {})
    enriched = orchestrator.enrich_context("Build a premium cinematic landing page with 3d hero animation", {})

    assert "cinematic_design" in skills
    assert "cinematic_design_prompt" in enriched
    assert "cinematic_analysis" in enriched
    assert "premium UI" in enriched["cinematic_design_prompt"]
    assert "Detected stack" in enriched["cinematic_design_prompt"]


def test_thinking_loop_includes_cinematic_context():
    loop = ThinkingLoop(LoopConfig(max_passes=1))
    prompt = loop._create_pass_prompt(
        1,
        PassType.IMPLEMENTATION,
        "Build premium landing page",
        {
            "cinematic_design_prompt": "Use spotlight, depth and smooth motion.",
            "cinematic_analysis": {"brightness_level": "dark", "motion_level": "subtle"},
        },
    )

    assert "Cinematic design guidance" in prompt
    assert "Use spotlight, depth and smooth motion." in prompt
    assert "Cinematic visual analysis metadata" in prompt
