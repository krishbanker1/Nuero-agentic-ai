"""
Tests for commit 4b45de3 improvements:
- Deterministic static-site scaffold
- Memory serialization robustness  
- Agent loop robustness
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest


class TestStaticSiteScaffold:
    """Test improved static site scaffold."""

    def test_static_site_scaffold_has_gitignore(self):
        """Static site scaffold should include .gitignore."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        plan = ProductionScaffolder.create_plan("Build a landing page")
        assert plan.stack == "static_site"
        
        paths = [f.path for f in plan.files]
        assert ".gitignore" in paths, ".gitignore should be in static site scaffold"

    def test_static_site_quality_gates(self):
        """Static site should have comprehensive quality gates."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        plan = ProductionScaffolder.create_plan("Build a marketing landing page")
        
        # Should have quality gates for vanilla JS, semantic HTML, CSS custom properties
        gates = " ".join(plan.quality_gates).lower()
        assert "vanilla" in gates or "no jquery" in gates
        assert "semantic" in gates
        assert "custom properties" in gates or "css custom" in gates

    def test_static_site_has_notes(self):
        """Static site scaffold should include helpful notes."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        plan = ProductionScaffolder.create_plan("Create a portfolio site")
        assert len(plan.notes) > 0, "Should have notes for developers"
        assert any("font" in note.lower() for note in plan.notes)

    def test_static_site_validation_commands(self):
        """Static site should have validation commands."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        plan = ProductionScaffolder.create_plan("Build a static website")
        assert len(plan.validation_commands) >= 1
        assert any("html" in cmd.lower() for cmd in plan.validation_commands)


class TestMemorySerialization:
    """Test memory serialization robustness."""

    def test_safe_json_loads_handles_corrupted_data(self):
        """_safe_json_loads should handle corrupted JSON gracefully."""
        from neuro.memory.task_store import TaskStore
        
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            store = TaskStore(db_path)
            
            # Test _safe_json_loads with corrupted data
            result = store._safe_json_loads(None, default=[])
            assert result == []
            
            result = store._safe_json_loads("", default={})
            assert result == {}
            
            result = store._safe_json_loads("not valid json{{{", default={"default": True})
            assert result == {"default": True}
            
            result = store._safe_json_loads('{"valid": true}')
            assert result == {"valid": True}
            
            store.close()
        finally:
            os.unlink(db_path)

    def test_safe_json_dumps_handles_datetime(self):
        """_safe_json_dumps should handle datetime objects."""
        from datetime import datetime
        from neuro.memory.task_store import TaskStore
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            store = TaskStore(db_path)
            
            result = store._safe_json_dumps({
                "date": datetime(2024, 1, 15, 12, 30, 0),
                "name": "test"
            })
            
            # Should return a valid JSON string
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed["name"] == "test"
            
            store.close()
        finally:
            os.unlink(db_path)

    def test_task_store_handles_corrupted_json_in_db(self):
        """TaskStore should gracefully handle corrupted JSON in database."""
        import sqlite3
        from neuro.memory.task_store import TaskStore
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            # Insert a task with corrupted JSON
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    goal_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    files_changed TEXT,
                    error TEXT,
                    duration_ms REAL,
                    model_used TEXT,
                    provider_used TEXT,
                    passes_used INTEGER,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Insert corrupted metadata
            conn.execute("""
                INSERT INTO tasks (goal, goal_hash, status, files_changed, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("test", "abc", "success", "not json", "2024-01-01", "also not json{{{"))
            conn.commit()
            conn.close()
            
            # TaskStore should handle this without crashing
            store = TaskStore(db_path)
            tasks = store.get_recent(limit=10)
            
            # Should return the task with default values for corrupted fields
            assert len(tasks) == 1
            assert tasks[0].goal == "test"
            # files_changed should be empty list, not crash
            assert isinstance(tasks[0].files_changed, list)
            # metadata should be empty dict, not crash
            assert isinstance(tasks[0].metadata, dict)
            
            store.close()
        finally:
            os.unlink(db_path)


class TestAgentLoopRobustness:
    """Test agent loop robustness improvements."""

    def test_safe_json_dumps_function_exists(self):
        """agent_loop should have _safe_json_dumps function."""
        from neuro.executor.agent_loop import _safe_json_dumps
        
        result = _safe_json_dumps({"test": "value"})
        assert result == '{"test": "value"}'
        
        # Should handle datetime
        from datetime import datetime
        result = _safe_json_dumps({"date": datetime.now()})
        assert '"date":' in result

    def test_safe_json_loads_function_exists(self):
        """agent_loop should have _safe_json_loads function."""
        from neuro.executor.agent_loop import _safe_json_loads
        
        assert _safe_json_loads(None, default=[]) == []
        assert _safe_json_loads("not json{{{", default={}) == {}
        assert _safe_json_loads('{"key": "value"}') == {"key": "value"}

    def test_logger_is_configured(self):
        """Agent loop should have logger configured."""
        from neuro.executor.agent_loop import logger
        assert logger is not None
        assert logger.name == "neuro.executor.agent_loop"


class TestProductionScaffolder:
    """Additional tests for production scaffolder."""

    def test_infer_stack_for_landing_page(self):
        """Should infer static_site for landing page."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        stack = ProductionScaffolder.infer_stack("Build a landing page")
        assert stack == "static_site"

    def test_infer_stack_for_portfolio(self):
        """Should infer static_site for portfolio."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        stack = ProductionScaffolder.infer_stack("Create my portfolio")
        assert stack == "static_site"

    def test_validate_workspace_missing_files(self):
        """validate_workspace should detect missing files."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only index.html
            Path(tmpdir, "index.html").write_text("<html></html>")
            
            # Use keyword that triggers static_site stack
            plan = ProductionScaffolder.create_plan("Build a landing page for my business")
            
            # Static site requires: SPEC.md, README.md, index.html, styles.css, app.js, .gitignore
            result = ProductionScaffolder.validate_workspace(tmpdir, plan)
            
            assert result["passed"] is False
            assert len(result["missing_required_files"]) > 0
            assert "SPEC.md" in result["missing_required_files"]
            assert "styles.css" in result["missing_required_files"]

    def test_validate_workspace_complete(self):
        """validate_workspace should pass for complete scaffold."""
        from neuro.skills.production_scaffolder import ProductionScaffolder
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create all required files
            Path(tmpdir, "SPEC.md").write_text("# Spec")
            Path(tmpdir, "README.md").write_text("# Readme")
            Path(tmpdir, "index.html").write_text("<html><body>test</body></html>")
            Path(tmpdir, "styles.css").write_text("body { color: red; }")
            Path(tmpdir, "app.js").write_text("// js")
            Path(tmpdir, ".gitignore").write_text("node_modules")
            
            # Use keyword that triggers static_site stack
            plan = ProductionScaffolder.create_plan("Build a landing page")
            result = ProductionScaffolder.validate_workspace(tmpdir, plan)
            
            assert result["passed"] is True
            assert len(result["missing_required_files"]) == 0
            assert len(result["empty_files"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])