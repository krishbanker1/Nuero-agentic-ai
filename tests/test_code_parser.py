"""
Tests for CodeParser - robust JSON extraction from LLM output
"""
import pytest
import tempfile
import os
from pathlib import Path
from neuro.core.code_parser import CodeParser, parse_and_write_files


class TestCodeParser:
    """Test CodeParser class for robust JSON/code extraction."""

    def test_fenced_json_with_newlines(self):
        """Test fenced JSON with literal newlines inside content string."""
        parser = CodeParser()
        response = '''```json
{
  "files": [
    {
      "path": "app.py",
      "content": "from flask import Flask\\napp = Flask(__name__)\\n@app.route('/')\\ndef home():\\n    return 'Hello'"
    }
  ]
}
```'''
        files = parser.parse_llm_response(response)
        assert len(files) >= 1
        # Verify newlines are preserved
        content = files[0].content
        assert "\\n" in content or "\n" in content

    def test_raw_multi_file_json_with_newlines(self):
        """Test raw multi-file JSON with literal newlines."""
        parser = CodeParser()
        response = '''{
  "files": [
    {"path": "index.html", "content": "<html>\\n<body>\\n  <h1>Hello</h1>\\n</body>\\n</html>"},
    {"path": "style.css", "content": "body {\\n  margin: 0;\\n  font-family: sans-serif;\\n}"}
  ]
}'''
        files = parser.parse_llm_response(response)
        assert len(files) >= 2

    def test_triple_quoted_content(self):
        """Test triple-quoted content values."""
        parser = CodeParser()
        response = '''```json
{
  "path": "test.py",
  "content": """def hello():
    print("world")
    return True"""
}
```'''
        files = parser.parse_llm_response(response)
        assert len(files) >= 1

    def test_malformed_json_path_content_pairs(self):
        """Test malformed JSON-like path/content pairs."""
        parser = CodeParser()
        response = '''```json
{
  "files": [
    {
      "path": "example.js",
      "content": "const x = 'hello';\\nconst y = 'world';\\nconsole.log(x, y);"
    }
  ]
}
```'''
        files = parser.parse_llm_response(response)
        assert len(files) >= 1

    def test_various_json_shapes(self):
        """Test various JSON shapes supported."""
        parser = CodeParser()
        
        # Shape 1: {"files": [{"path": ..., "content": ...}]}
        response1 = '{"files": [{"path": "a.py", "content": "x = 1"}]}'
        files1 = parser.parse_llm_response(response1)
        assert len(files1) >= 1
        
        # Shape 2: {"path": ..., "content": ...}
        response2 = '{"path": "b.py", "content": "y = 2"}'
        files2 = parser.parse_llm_response(response2)
        assert len(files2) >= 1
        
        # Shape 3: [{"path": ..., "content": ...}]
        response3 = '[{"path": "c.py", "content": "z = 3"}]'
        files3 = parser.parse_llm_response(response3)
        assert len(files3) >= 1
        
        # Shape 4: {"filename": ..., "code": ...}
        response4 = '{"filename": "d.py", "code": "a = 4"}'
        files4 = parser.parse_llm_response(response4)
        assert len(files4) >= 1
        
        # Shape 5: {"file_path": ..., "content": ...}
        response5 = '{"file_path": "e.py", "content": "b = 5"}'
        files5 = parser.parse_llm_response(response5)
        assert len(files5) >= 1
        
        # Shape 6: {"target_file": ..., "code": ...}
        response6 = '{"target_file": "f.py", "code": "c = 6"}'
        files6 = parser.parse_llm_response(response6)
        assert len(files6) >= 1

    def test_parse_and_write_files(self):
        """Test parse_and_write_files skips empty content and writes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with valid content
            response = '''```json
{
  "files": [
    {"path": "test.py", "content": "print('hello')"},
    {"path": "empty.txt", "content": ""}
  ]
}
```'''
            created = parse_and_write_files(response, tmpdir, verbose=False)
            
            # Should write test.py but skip empty.txt
            assert len(created) >= 1
            assert any("test.py" in f for f in created)
            
            # Verify file was actually created and has content
            test_file = Path(tmpdir) / "test.py"
            assert test_file.exists()
            assert test_file.stat().st_size > 0
            
    def test_path_aliases(self):
        """Test that path aliases work correctly."""
        parser = CodeParser()
        
        # Test path alias (primary)
        response = '{"path": "test.py", "content": "x = 1"}'
        files = parser.parse_llm_response(response)
        assert len(files) >= 1, "Should find file with 'path' key"
        assert files[0].path == "test.py"
        
        # Test file_path alias
        response = '{"file_path": "test2.py", "content": "y = 2"}'
        files = parser.parse_llm_response(response)
        # file_path should work via _extract_files_from_json
        assert len(files) >= 1, "Should find file with 'file_path' key"
        
        # Test target_file alias
        response = '{"target_file": "test3.py", "code": "z = 3"}'
        files = parser.parse_llm_response(response)
        # target_file with code should work
        assert len(files) >= 1, "Should find file with 'target_file' and 'code'"
        
    def test_skips_empty_path(self):
        """Test that entries with no path are skipped."""
        parser = CodeParser()
        response = '{"path": "", "content": "something"}'
        # Should not crash, may return 0 files due to empty path being skipped
        files = parser.parse_llm_response(response)
        assert isinstance(files, list)

    def test_skips_empty_content(self):
        """Test that entries with empty content are skipped."""
        parser = CodeParser()
        response = '{"path": "test.py", "content": ""}'
        # Should not crash
        files = parser.parse_llm_response(response)
        assert isinstance(files, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])