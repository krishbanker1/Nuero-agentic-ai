"""
Tests for ultimate integration - import, capabilities, skill matching
"""
import pytest
from pathlib import Path


class TestUltimateImport:
    """Test that ultimate package imports without errors."""

    def test_import_neuro_ultimate(self):
        """Test import neuro.ultimate succeeds."""
        import neuro.ultimate
        assert neuro.ultimate is not None

    def test_ultimate_registry_class_exists(self):
        """Test NeuroUltimateRegistry class is accessible."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        assert hasattr(NeuroUltimateRegistry, 'MCP_SERVERS')
        assert hasattr(NeuroUltimateRegistry, 'get_all_capabilities')
        assert hasattr(NeuroUltimateRegistry, 'match_skill_for_task')

    def test_import_ultimate_orchestrator(self):
        """Test ultimate orchestrator imports correctly."""
        from neuro.ultimate.orchestrator import TaskType, UltimateOrchestrator
        
        # TaskType should exist
        assert hasattr(TaskType, 'CODING')


class TestUltimateCapabilities:
    """Test ultimate capabilities are properly structured."""

    def test_pal_mcp_capabilities_flat_list(self):
        """Test pal_mcp_server capabilities are a flat list of strings."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        pal_server = NeuroUltimateRegistry.MCP_SERVERS.get("pal_mcp_server")
        assert pal_server is not None
        
        capabilities = pal_server.get("capabilities", [])
        
        # Verify it's a flat list
        assert isinstance(capabilities, list)
        for cap in capabilities:
            assert isinstance(cap, str), f"Expected string, got {type(cap)}: {cap}"

    def test_all_mcp_capabilities_flat(self):
        """Test all MCP server capabilities are flat lists."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        for name, server in NeuroUltimateRegistry.MCP_SERVERS.items():
            capabilities = server.get("capabilities", [])
            assert isinstance(capabilities, list), f"{name} capabilities not a list"
            for cap in capabilities:
                assert isinstance(cap, str), f"{name} capability not string: {cap}"

    def test_three_d_graphics_skills_list(self):
        """Test THREE_D_GRAPHICS_SKILLS is a list of dicts."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        skills = NeuroUltimateRegistry.THREE_D_GRAPHICS_SKILLS
        assert isinstance(skills, list)
        
        for skill in skills:
            assert isinstance(skill, dict)
            assert "name" in skill
            assert "triggers" in skill


class TestUltimateSkillMatching:
    """Test enterprise/API/database/design task skill matching."""

    def test_match_skills_for_enterprise_task(self):
        """Test enterprise task selects relevant skills."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        # Test enterprise app task
        matched = NeuroUltimateRegistry.match_skill_for_task(
            "Build an enterprise REST API with database backend"
        )
        assert isinstance(matched, list)

    def test_match_skills_for_api_task(self):
        """Test API task selects relevant skills."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        matched = NeuroUltimateRegistry.match_skill_for_task(
            "Create a REST API endpoint for user authentication"
        )
        assert isinstance(matched, list)

    def test_match_skills_for_database_task(self):
        """Test database task selects relevant skills."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        matched = NeuroUltimateRegistry.match_skill_for_task(
            "Design a PostgreSQL schema for user management"
        )
        assert isinstance(matched, list)

    def test_match_skills_for_design_task(self):
        """Test design task selects relevant skills."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        matched = NeuroUltimateRegistry.match_skill_for_task(
            "Create a Figma design for the landing page"
        )
        assert isinstance(matched, list)

    def test_match_skills_for_frontend_task(self):
        """Test frontend task selects relevant skills."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        matched = NeuroUltimateRegistry.match_skill_for_task(
            "Build a React component with animations"
        )
        assert isinstance(matched, list)


class TestSkillOrchestratorEnrichment:
    """Test SkillOrchestrator enriches context with ultimate analysis."""

    def test_skill_orchestrator_initialization(self):
        """Test SkillOrchestrator initializes correctly."""
        from neuro.skills.skill_orchestrator import SkillOrchestrator
        
        orchestrator = SkillOrchestrator(verbose=False)
        assert orchestrator is not None
        assert hasattr(orchestrator, 'active_skills')

    def test_enrich_context_returns_dict(self):
        """Test enrich_context returns a dictionary."""
        from neuro.skills.skill_orchestrator import SkillOrchestrator
        
        orchestrator = SkillOrchestrator(verbose=False)
        enriched = orchestrator.enrich_context(
            "Build a web app",
            {"task": "example"}
        )
        assert isinstance(enriched, dict)

    def test_detect_skills_returns_list(self):
        """Test detect_skills returns a list of skill names."""
        from neuro.skills.skill_orchestrator import SkillOrchestrator
        
        orchestrator = SkillOrchestrator(verbose=False)
        detected = orchestrator.detect_skills("Build a web app")
        assert isinstance(detected, list)


class TestUltimateModelRegistry:
    """Test ultimate model registry."""

    def test_model_registry_imports(self):
        """Test model registry imports correctly."""
        from neuro.ultimate.model_registry import ModelProvider
        
        assert hasattr(ModelProvider, 'GROQ')
        assert hasattr(ModelProvider, 'OPENROUTER')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])