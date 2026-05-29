"""
Robust Code Parser - Enterprise-grade extraction from LLM output
Handles all edge cases: newlines, escaping, malformed JSON, code blocks

This is the CORE FIX for Nuero - replaces ad-hoc parsing with proven strategies.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ParsedFile:
    """Represents a single parsed file."""
    path: str
    content: str
    file_type: str
    confidence: float

class CodeParser:
    """
    Robust code extraction from LLM responses.
    
    Strategies used (in order):
    1. Strict JSON parsing (if valid)
    2. Flexible JSON with newline fixing
    3. Regex-based file extraction from code blocks
    4. Heuristic content detection
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def parse_llm_response(self, response: str) -> List[ParsedFile]:
        """Main entry point - parse LLM response into files."""
        if self.verbose:
            print(f"🔍 Parsing response ({len(response)} chars)...")
        
        # Strategy 1: Strict JSON
        files = self._try_strict_json(response)
        if files:
            if self.verbose:
                print(f"✅ Strategy 1 (strict JSON): {len(files)} files")
            return files
        
        # Strategy 2: Flexible JSON with newline fixing
        files = self._try_flexible_json(response)
        if files:
            if self.verbose:
                print(f"✅ Strategy 2 (flexible JSON): {len(files)} files")
            return files
        
        # Strategy 3: Code blocks
        files = self._try_code_blocks(response)
        if files:
            if self.verbose:
                print(f"✅ Strategy 3 (code blocks): {len(files)} files")
            return files
        
        # Strategy 4: Embedded JSON-like
        files = self._try_embedded_json(response)
        if files:
            if self.verbose:
                print(f"✅ Strategy 4 (embedded JSON): {len(files)} files")
            return files
        
        return []
    
    def _try_strict_json(self, text: str) -> List[ParsedFile]:
        """Strategy 1: Parse strict JSON."""
        try:
            json_blocks = re.findall(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
            if not json_blocks:
                if text.strip().startswith('{') and '"files"' in text:
                    json_blocks = [text]
            
            for block in json_blocks:
                try:
                    data = json.loads(block)
                    if files := self._extract_files_from_json(data):
                        return files
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            if self.verbose:
                print(f"   Strategy 1 failed: {e}")
        return []
    
    def _try_flexible_json(self, text: str) -> List[ParsedFile]:
        """Strategy 2: JSON with fixes for newlines.
        
        This is the MAIN FIX - handles the case where AI puts actual newlines
        inside JSON string values (which is invalid JSON).
        """
        try:
            json_blocks = re.findall(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
            
            for block in json_blocks:
                # Strategy 2a: Fix actual newlines by escaping them
                fixed = self._fix_json_newlines(block)
                try:
                    data = json.loads(fixed)
                    if files := self._extract_files_from_json(data):
                        return files
                except:
                    pass
                
                # Strategy 2b: Try with escaped newlines added
                try:
                    # Replace actual newlines with \n in the entire block
                    lines = block.split('\n')
                    if len(lines) > 2:
                        # Check if this looks like a JSON with broken content
                        fixed = block.replace('\n', '\\n')
                        data = json.loads(fixed)
                        if files := self._extract_files_from_json(data):
                            return files
                except:
                    pass
                
                # Strategy 2c: Manual JSON extraction using state machine
                files = self._extract_files_manual(block)
                if files:
                    return files
                    
        except Exception as e:
            if self.verbose:
                print(f"   Strategy 2 failed: {e}")
        return []
    
    def _extract_files_manual(self, json_str: str) -> List[ParsedFile]:
        """Manual extraction using state machine - handles broken JSON.
        
        This is the ROBUST fallback that can extract content even from
        malformed JSON where newlines are not escaped inside strings.
        """
        files = []
        
        # Find all file objects by looking for path/content pairs
        # We'll use a state machine to track JSON structure
        
        # Find positions of "path" keys
        path_positions = []
        for m in re.finditer(r'''["']path["']\s*:''', json_str):
            path_positions.append(m.start())
        
        for pos in path_positions:
            # Extract the path value (what comes after "path":)
            search_area = json_str[pos:pos+500]
            path_match = re.search(r':\s*["\']([^"\']+)["\']', search_area)
            if not path_match:
                continue
            path = path_match.group(1)
            
            # Now find the content - it comes after this path
            # The content might span multiple lines
            content_start = pos + path_match.end()
            content_search = json_str[content_start:content_start+3000]
            
            # Find where content ends - look for the closing } of this file object
            # But be careful not to go into nested structures
            
            content = ""
            content_match = re.search(r'''["']content["']\s*:\s*"""([\s\S]*?)"""''', content_search)
            if not content_match:
                content_match = re.search(r'''["']content["']\s*:\s*(.+?)(?=,\s*[}\]])''', content_search, re.DOTALL)
            
            if content_match:
                content = content_match.group(1).strip()
                # Remove surrounding quotes if present
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
                elif content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]
                # Unescape
                content = content.replace('\\n', '\n').replace('\\"', '"')
            
            fname, ftype = self._detect_file_info(content, "", path)
            files.append(ParsedFile(
                path=path,
                content=content,
                file_type=ftype,
                confidence=0.7
            ))
        
        return files
    
    def _fix_json_newlines(self, json_str: str) -> str:
        """Fix actual newlines inside JSON string values.
        
        IMPORTANT: We need to ESCAPE them (\\n) so JSON parses correctly,
        then the content will have proper newlines when extracted.
        """
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                escape_next = True
                result.append(char)
                i += 1
                continue
            
            if char == '"':
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            # If we're inside a string and hit a newline, escape it
            if in_string and char == '\n':
                result.append('\\n')
                i += 1
                continue
            
            if in_string and char == '\r':
                result.append('\\r')
                i += 1
                continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def _fix_json_manually(self, json_str: str) -> str:
        """Manually fix common JSON issues."""
        lines = json_str.split('\n')
        result = []
        in_string = False
        escape_next = False
        
        for line in lines:
            fixed_line = []
            for char in line:
                if escape_next:
                    escape_next = False
                    fixed_line.append(char)
                    continue
                
                if char == '\\':
                    escape_next = True
                    fixed_line.append(char)
                    continue
                
                if char == '"':
                    in_string = not in_string
                    fixed_line.append(char)
                    continue
                
                if in_string:
                    fixed_line.append(char)
                elif char not in ' \t':
                    fixed_line.append(char)
            
            result.append(''.join(fixed_line))
        
        return '\n'.join(result)
    
    def _try_code_blocks(self, text: str) -> List[ParsedFile]:
        """Strategy 3: Extract from markdown code blocks."""
        files = []
        
        code_blocks = re.findall(
            r'```(\w*)\s*\n?(.*?)```',
            text,
            re.DOTALL | re.IGNORECASE
        )
        
        for lang, content in code_blocks:
            content = content.strip()
            if len(content) < 20:
                continue
            
            if lang.lower() in ('json',) or content.startswith('{') or content.startswith('['):
                continue
            
            fname, ftype = self._detect_file_info(content, lang)
            
            if fname:
                files.append(ParsedFile(
                    path=fname,
                    content=content,
                    file_type=ftype,
                    confidence=0.7
                ))
        
        return files
    
    def _try_embedded_json(self, text: str) -> List[ParsedFile]:
        """Strategy 4: Find embedded JSON-like structures with proper content extraction."""
        files = []
        
        # Look for JSON blocks that might have been broken
        # Pattern: path followed by content, handling broken newlines
        pattern = r'''["']path["']\s*:\s*["']([^"']+)["']'''
        paths = re.findall(pattern, text)
        
        if not paths:
            return files
        
        # For each path, find the associated content
        for path in paths:
            # Find the position of this path in the text
            path_pos = text.find(f'"path": "{path}"')
            if path_pos == -1:
                path_pos = text.find(f"'path': '{path}'")
            if path_pos == -1:
                continue
            
            # Look for content after this path
            search_start = path_pos
            search_end = min(path_pos + 2000, len(text))
            
            # Try to find content value
            content = ""
            
            # Pattern 1: After path, look for content
            after_path = text[search_start:search_end]
            
            # Match content that starts after "content":
            content_patterns = [
                r'''["']content["']\s*:\s*(?:"""([\s\S]*?)"""|[']([^'}]+)['])''',
                r'''content["']\s*:\s*["']([^"']*(?:\\.[^"']*)*)["']''',
            ]
            
            for cp in content_patterns:
                cm = re.search(cp, after_path, re.DOTALL)
                if cm:
                    # Try to get content from different groups
                    content = cm.group(1) or cm.group(2) or ""
                    if content:
                        break
            
            # Clean up the content - it might have actual newlines
            if content:
                # Unescape any escaped newlines first
                content = content.replace('\\n', '\n')
                
                # Try to unescape more if needed
                try:
                    # Check if there are still newlines that need handling
                    if '\n' in content:
                        # The JSON might have broken newlines - try to fix
                        pass
                except:
                    pass
            
            fname, ftype = self._detect_file_info(content, "", path)
            files.append(ParsedFile(
                path=path,
                content=content if content else "",
                file_type=ftype,
                confidence=0.6
            ))
        
        return files
    
    def _extract_files_from_json(self, data: Any) -> List[ParsedFile]:
        """Extract files from parsed JSON."""
        files = []
        
        if isinstance(data, dict):
            if 'files' in data:
                for item in data['files']:
                    if isinstance(item, dict):
                        path = item.get('path', '')
                        content = item.get('content', '')
                        if path and content:
                            fname, ftype = self._detect_file_info(content, "", path)
                            files.append(ParsedFile(
                                path=path,
                                content=self._clean_content(content),
                                file_type=ftype,
                                confidence=0.9
                            ))
            elif 'path' in data and 'content' in data:
                path = data['path']
                content = data['content']
                fname, ftype = self._detect_file_info(content, "", path)
                files.append(ParsedFile(
                    path=path,
                    content=self._clean_content(content),
                    file_type=ftype,
                    confidence=0.9
                ))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    path = item.get('path', item.get('file', ''))
                    content = item.get('content', item.get('code', ''))
                    if path and content:
                        fname, ftype = self._detect_file_info(content, "", path)
                        files.append(ParsedFile(
                            path=path,
                            content=self._clean_content(content),
                            file_type=ftype,
                            confidence=0.7
                        ))
        
        return files
    
    def _clean_content(self, content: str) -> str:
        """Clean up content."""
        if not content:
            return ""
        
        content = str(content)
        
        if content.startswith('"""') and content.endswith('"""'):
            content = content[3:-3]
        elif content.startswith("'''") and content.endswith("'''"):
            content = content[3:-3]
        
        content = content.replace('\\n', '\n').replace('\\r', '\r').replace('\\"', '"')
        content = content.replace('\\\\n', '\n').replace('\\\\r', '\r').replace('\\\\"', '"')
        
        return content.strip()
    
    def _detect_file_info(self, content: str, lang: str, existing_path: str = "") -> Tuple[str, str]:
        """Detect file type and suggest filename."""
        if existing_path:
            ext = Path(existing_path).suffix.lower()
            ftype = self._ext_to_type(ext)
            return existing_path, ftype
        
        if lang:
            lang = lang.lower()
            if lang in ('py', 'python'):
                return self._suggest_filename(content, 'python')
            elif lang in ('js', 'javascript'):
                return self._suggest_filename(content, 'javascript')
            elif lang in ('html', 'htm'):
                return 'index.html', 'html'
            elif lang in ('css',):
                return 'style.css', 'css'
        
        content_lower = content.lower()
        
        if re.search(r'from\s+flask|import\s+flask|@app\.route|def\s+\w+\(', content):
            return self._suggest_filename(content, 'python')
        elif re.search(r'<html|<!doctype\s+html|<head>|<body', content_lower):
            return 'index.html', 'html'
        elif re.search(r'body\s*\{|[\.#]\w+\s*\{|@media', content):
            return 'style.css', 'css'
        elif re.search(r'const\s+\w+|let\s+\w+|function\s+\w+|=>\s*\{', content):
            return self._suggest_filename(content, 'javascript')
        
        return self._suggest_filename(content, 'text')
    
    def _suggest_filename(self, content: str, ftype: str) -> Tuple[str, str]:
        """Suggest filename."""
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match and ftype == 'python':
            return f"{class_match.group(1).lower()}.py", 'python'
        
        defaults = {
            'python': 'app.py',
            'javascript': 'app.js',
            'html': 'index.html',
            'css': 'style.css',
            'text': 'output.txt'
        }
        
        return defaults.get(ftype, 'output.txt'), ftype
    
    def _ext_to_type(self, ext: str) -> str:
        """Map extension to type."""
        mapping = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.html': 'html', '.htm': 'html', '.css': 'css',
            '.sql': 'sql', '.json': 'json', '.md': 'markdown',
        }
        return mapping.get(ext, 'text')


def parse_and_write_files(response: str, output_dir: str = ".", verbose: bool = True) -> List[str]:
    """Parse LLM response and write files."""
    parser = CodeParser(verbose=verbose)
    files = parser.parse_llm_response(response)
    
    output_path = Path(output_dir)
    created = []
    
    for pf in files:
        full_path = output_path / pf.path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(pf.content)
        created.append(str(full_path))
        
        if verbose:
            print(f"   ✅ {pf.path}")
    
    return created


if __name__ == '__main__':
    parser = CodeParser(verbose=True)
    
    test = '''
```json
{
  "files": [
    {"path": "app.py", "content": "from flask import Flask\\napp = Flask(__name__)"},
    {"path": "index.html", "content": "<html>\\n<body>Hello</body>\\n</html>"}
  ]
}
```
'''
    print("\n=== Test ===")
    files = parser.parse_llm_response(test)
    print(f"Found {len(files)} files")
    for f in files:
        print(f"  - {f.path} ({f.file_type})")