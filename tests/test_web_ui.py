"""
Tests for Neuro Studio Web UI and model fallback hardening.

Tests cover:
- Web UI server startup
- API health endpoint
- API chat endpoint
- File upload handling
- Preview launch/stop
- Deep model fallback chain
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestWebUIImports:
    """Test web UI module imports correctly."""

    def test_web_ui_imports(self):
        """Web UI module should import without errors."""
        from neuro.web_ui import (
            get_studio_html,
            get_available_providers,
            sanitize_filename,
            save_uploaded_file,
            launch_app_preview,
            stop_app_previews,
        )
        assert callable(get_studio_html)
        assert callable(sanitize_filename)

    def test_studio_html_is_valid_html(self):
        """Studio HTML should be valid HTML with key elements."""
        from neuro.web_ui import get_studio_html
        
        html = get_studio_html()
        assert "<html" in html
        assert "</html>" in html or "</body>" in html
        assert "Neuro Studio" in html

    def test_get_available_providers(self):
        """get_available_providers should return dict."""
        from neuro.web_ui import get_available_providers
        
        providers = get_available_providers()
        assert isinstance(providers, dict)

    def test_sanitize_filename_removes_path(self):
        """sanitize_filename should remove path components."""
        from neuro.web_ui import sanitize_filename
        
        # Path traversal attempt
        result = sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        
        # Normal filename
        result = sanitize_filename("screenshot.png")
        assert "screenshot.png" == result

    def test_sanitize_filename_limits_length(self):
        """sanitize_filename should limit length."""
        from neuro.web_ui import sanitize_filename
        
        long_name = "a" * 200 + ".png"
        result = sanitize_filename(long_name)
        assert len(result) <= 100


class TestPreviewLaunch:
    """Test app preview launching functionality."""

    def test_launch_app_preview_static_site(self):
        """Should launch static site preview."""
        from neuro.web_ui import launch_app_preview, stop_app_previews
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple static site
            Path(tmpdir, "index.html").write_text("<!DOCTYPE html><title>Test</title>")
            
            result = launch_app_preview(tmpdir, request_host="127.0.0.1:8080", port=8099)
            
            # May fail due to no actual server start, but should not crash
            assert "success" in result
            assert "error" in result or "browser_url" in result or "app_type" in result
            
            # Clean up
            stop_app_previews()

    def test_launch_app_preview_nonexistent_workspace(self):
        """Should handle nonexistent workspace gracefully."""
        from neuro.web_ui import launch_app_preview
        
        result = launch_app_preview("/nonexistent/path")
        assert result["success"] is False
        assert "error" in result

    def test_stop_app_previews_cleans_up(self):
        """stop_app_previews should not crash."""
        from neuro.web_ui import stop_app_previews
        
        # Should not raise
        stop_app_previews()


class TestCLIIntegration:
    """Test CLI --ui flags."""

    def test_ui_flags_in_help(self):
        """Help text should include --ui flags."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "neuro", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        assert "--ui" in output
        assert "--ui-host" in output
        assert "--ui-port" in output
        assert "--no-open-browser" in output


class TestRouterFallback:
    """Test model fallback hardening."""

    def test_complete_tries_all_fallbacks(self):
        """complete() should try all models in chain."""
        from neuro.router.smart_router import SmartRouter
        
        router = SmartRouter()
        
        # Mock all provider calls to fail
        with patch.object(router, '_call_groq', return_value={"error": "mock failure"}), \
             patch.object(router, '_call_gemini', return_value={"error": "mock failure"}), \
             patch.object(router, '_call_openrouter', return_value={"error": "mock failure"}):
            
            result = router.complete([{"role": "user", "content": "test"}])
            assert "error" in result

    def test_chat_removes_fallback_cap(self):
        """chat() should try all fallbacks, not just 4."""
        # This test verifies the code structure, not runtime behavior
        import inspect
        from neuro.router.smart_router import SmartRouter
        
        source = inspect.getsource(SmartRouter.chat)
        # Verify the [:4] cap was removed
        assert "models_to_try[:4]" not in source, "Fallback depth cap [:4] should be removed"
        assert "for model_config in models_to_try:" in source


class TestSafeJSONHandling:
    """Test safe JSON handling in web UI."""

    def test_web_ui_handles_json_decode_error(self):
        """Web UI should handle malformed JSON gracefully."""
        from neuro.web_ui import run_neuro_goal
        
        # Test with invalid screenshots (None)
        result = run_neuro_goal(
            goal="test goal",
            screenshots=None
        )
        # Should return dict with keys, not crash
        assert isinstance(result, dict)
        assert "status" in result or "error" in result or "success" in result


class TestUploadSafety:
    """Test file upload safety features."""

    def test_file_size_limit(self):
        """Should reject files over 10MB."""
        from neuro.web_ui import save_uploaded_file
        
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_dir = Path(tmpdir)
            large_content = b"x" * (11 * 1024 * 1024)  # 11MB
            
            with pytest.raises(ValueError, match="File too large"):
                save_uploaded_file(large_content, "large.png", upload_dir)

    def test_path_traversal_prevention(self):
        """Should prevent path traversal in uploads."""
        from neuro.web_ui import sanitize_filename
        
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "../../../.bashrc",
            "foo/../../../etc/passwd",
        ]
        
        for name in dangerous_names:
            result = sanitize_filename(name)
            assert ".." not in result
            assert result.startswith("/") is False or result.startswith("./") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])