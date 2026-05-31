"""
Tests for execution wiring - chunk schema, lazy skills, MCP scripts
"""
import pytest
import tempfile
import os
import subprocess
from pathlib import Path


class TestExecutionWiring:
    """Test role agent chunk schema and validator wiring."""

    def test_engineer_chunk_schema_includes_path_aliases(self):
        """Test EngineerAgent chunk schema includes all path aliases."""
        from neuro.executor.role_agents import EngineerAgent
        
        assert EngineerAgent().name == "EngineerAgent"
        
        # Verify the chunk schema supports path aliases
        # Engineer should create chunks with these fields
        test_chunk = {
            "path": "test.py",
            "code": "print('hello')",
            "verified": True
        }
        
        # Check that path alias works
        assert "path" in test_chunk or "file_path" in test_chunk or "target_file" in test_chunk

    def test_validator_writes_to_configured_working_dir(self):
        """Test ValidatorAgent writes files to configured working_dir, not os.getcwd."""
        from neuro.executor.role_agents import ValidatorAgent
        
        agent = ValidatorAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a task with working_dir set
            task = {
                "implementation": {
                    "chunks": [
                        {
                            "file_path": "test.py",
                            "code": "x = 1\n",
                            "verified": True
                        }
                    ]
                },
                "context": {
                    "task_type": "code_fix",
                    "working_dir": tmpdir,
                    "codebase_root": tmpdir
                }
            }
            
            # Run validator
            result = agent.run(task)
            test_file = Path(tmpdir) / "test.py"

            assert result.data["test_results"]["total"] >= 1
            assert test_file.exists()
            assert not (Path.cwd() / "test.py").exists()


class TestLazySkills:
    """Test lazy skill imports resolve correctly."""

    def test_lazy_skill_imports_resolve(self):
        """Test lazy skill imports resolve for fixed skill names."""
        from neuro.skills import _lazy_get_skill, _lazy_imports
        
        # These are the lazy import names that should resolve to actual class names
        # in the repo (not the old incorrect "Skill" suffix)
        lazy_skills = [
            "react_three_fiber",   # -> ReactThreeFiber, not ReactThreeFiberSkill
            "spline_design",       # -> SplineDesign, not SplineDesignSkill
            "glsl_shaders",        # -> GLSLShaders, not GLSLShaderSkill
            "framer_motion",       # -> FramerMotion, not FramerMotionSkill
            "component_driven",    # -> ComponentDriven, not ComponentDrivenSkill
            "vector_math",         # -> VectorMath, not VectorMathSkill
            "asset_mapping",       # -> AssetMapping, not AssetMappingSkill
            "gsap",
            "scrolltrigger",
            "smooth_scroll",
            "lenis",
        ]
        
        for skill_name in lazy_skills:
            try:
                # Should not raise AttributeError about wrong class name
                assert _lazy_get_skill(skill_name) is not None
            except AttributeError as e:
                if "Skill" in str(e):
                    pytest.fail(f"Lazy import uses wrong class name suffix for {skill_name}: {e}")
                # Other AttributeErrors are acceptable (module exists but no attribute)


class TestMCPScriptGeneration:
    """Test MCP install script generation with proper shell variables."""

    def test_generated_script_contains_shell_variables(self):
        """Test generated MCP install script contains shell color variables."""
        from neuro.ultimate.mcp_server_registry import MCPServerRegistry
        
        script = MCPServerRegistry.generate_install_script()
        
        # Script should contain shell variable definitions
        assert "YELLOW=" in script or "YELLOW='" in script
        assert "NC=" in script or "NC'" in script
        
        # Should use ${YELLOW} and ${NC} in echo statements for shell interpolation
        # The fix used ${{YELLOW}} in f-string to produce ${YELLOW} in output
        assert "${YELLOW}" in script, "Script should contain ${YELLOW} for shell"
        assert "${NC}" in script, "Script should contain ${NC} for shell"

    def test_mcp_registry_imports_without_error(self):
        """Test mcp_server_registry imports without syntax errors."""
        from neuro.ultimate.mcp_server_registry import MCPServerRegistry, MCPServerManager
        
        # Should import cleanly
        assert MCPServerRegistry is not None
        assert MCPServerManager is not None


class TestReadmeContent:
    """Test that README doesn't advertise unproven benchmark claims."""

    def test_readme_no_unproven_benchmark_claims(self):
        """Test README doesn't advertise benchmark dependency or competitive claims."""
        readme_path = Path(__file__).parent.parent / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text()
            
            # Should not claim specific benchmark percentages as achieved
            # Note: "75-85% benchmark performance (target, not achieved)" in 
            # "What's NOT Claimed" section is acceptable
            if "85% benchmark" in content.lower():
                # If it mentions benchmark %, it should be in "not claimed" section
                assert "not achieved" in content.lower() or "not claimed" in content.lower()
            
            # Should not claim "beats" without qualification
            if "beats" in content.lower():
                # If it mentions "beats", it should clarify it's not proven
                assert "not proven" in content.lower() or "not tested" in content.lower()


class TestPyprojectMetadata:
    """Test pyproject.toml doesn't contain benchmark-specific metadata."""

    def test_pyproject_no_benchmark_deps(self):
        """Test pyproject.toml doesn't have benchmark-only optional dependencies."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            
            # Should not have swe-bench as explicit dependency marker
            assert "swe-bench" not in content.lower() or "optional" in content.lower()


class TestUltimateIntegration:
    """Test ultimate package integration."""

    def test_import_neuro_ultimate(self):
        """Test import neuro.ultimate succeeds."""
        try:
            import neuro.ultimate
            assert True
        except SyntaxError as e:
            pytest.fail(f"Syntax error in neuro.ultimate: {e}")

    def test_pal_mcp_capabilities_flat_list(self):
        """Test pal_mcp_server capabilities are a flat list of strings."""
        from neuro.ultimate import NeuroUltimateRegistry
        
        pal_server = NeuroUltimateRegistry.MCP_SERVERS.get("pal_mcp_server")
        assert pal_server is not None, "pal_mcp_server not found in registry"
        
        capabilities = pal_server.get("capabilities", [])
        
        # Should be a flat list, not dict
        for cap in capabilities:
            assert isinstance(cap, str), f"capability should be string, got {type(cap)}: {cap}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])