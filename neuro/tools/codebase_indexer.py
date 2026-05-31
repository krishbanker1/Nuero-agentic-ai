"""Codebase Indexer - Index entire project for context using FREE embeddings"""
from typing import Dict, List
from dataclasses import dataclass
import os

class CodebaseIndexer:
    """
    Index entire codebase for context-aware AI generation.
    FREE - uses local embeddings or simple keyword matching.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.index: Dict[str, FileInfo] = {}
        self.file_tree: Dict[str, List[str]] = {}
        self.symbols: Dict[str, List[Symbol]] = {}
        self._build_index()
    
    def _build_index(self):
        """Build full codebase index."""
        print(f"Indexing {self.root_dir}...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden and common ignore dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']]
            
            for file in files:
                if self._should_index(file):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.root_dir)
                    
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Index file info
                        self.index[rel_path] = FileInfo(
                            path=rel_path,
                            content=content,
                            language=self._detect_language(file),
                            size=len(content),
                            lines=len(content.split('\n'))
                        )
                        
                        # Index symbols (functions, classes)
                        self._index_symbols(rel_path, content)
                        
                    except Exception as e:
                        print(f"Error indexing {rel_path}: {e}")
        
        print(f"Indexed {len(self.index)} files")
    
    def _should_index(self, file: str) -> bool:
        """Check if file should be indexed."""
        exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json', 
                '.md', '.yaml', '.yml', '.sh', '.sql', '.go', '.rs', '.java'}
        return any(file.endswith(ext) for ext in exts)
    
    def _detect_language(self, file: str) -> str:
        """Detect programming language."""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript', '.html': 'html',
            '.css': 'css', '.json': 'json', '.md': 'markdown',
            '.yaml': 'yaml', '.yml': 'yaml', '.sh': 'bash',
            '.sql': 'sql', '.go': 'go', '.rs': 'rust', '.java': 'java'
        }
        for ext, lang in lang_map.items():
            if file.endswith(ext):
                return lang
        return 'unknown'
    
    def _index_symbols(self, path: str, content: str):
        """Extract functions, classes from code."""
        lines = content.split('\n')
        
        # Simple patterns
        patterns = [
            (r'def (\w+)\(', 'function'),
            (r'class (\w+)', 'class'),
            (r'function (\w+)\(', 'function'),
            (r'const (\w+) =', 'const'),
            (r'(\w+):\s*async\s*\(', 'async_function'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, sym_type in patterns:
                import re
                match = re.search(pattern, line)
                if match:
                    name = match.group(1)
                    if path not in self.symbols:
                        self.symbols[path] = []
                    self.symbols[path].append(Symbol(
                        name=name,
                        type=sym_type,
                        line=i + 1,
                        context=line.strip()
                    ))
    
    def get_relevant_files(self, query: str, max_files: int = 10) -> List[str]:
        """Get files relevant to query using keyword matching."""
        query_words = set(query.lower().split())
        scores = {}
        
        for path, info in self.index.items():
            score = 0
            content_lower = info.content.lower()
            
            # Word matching
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
                if word in path.lower():
                    score += 5  # Boost for filename match
            
            # Symbol matching
            if path in self.symbols:
                for sym in self.symbols[path]:
                    if any(word in sym.name.lower() for word in query_words):
                        score += 10
            
            if score > 0:
                scores[path] = score
        
        # Sort by score
        sorted_files = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return sorted_files[:max_files]
    
    def get_context(self, query: str, max_tokens: int = 4000) -> str:
        """Get relevant context for query."""
        files = self.get_relevant_files(query)
        
        context_parts = []
        total_chars = 0
        
        for file in files:
            info = self.index[file]
            content = f"\n# File: {file}\n{info.content}\n"
            
            if total_chars + len(content) > max_tokens * 4:
                break
            
            context_parts.append(content)
            total_chars += len(content)
        
        return "\n".join(context_parts)
    
    def get_file_tree(self) -> str:
        """Get directory tree."""
        tree = []
        for path in sorted(self.index.keys()):
            depth = path.count(os.sep)
            tree.append("  " * depth + "📄 " + os.path.basename(path))
        return "\n".join(tree[:100])  # Limit to 100 files


@dataclass
class FileInfo:
    path: str
    content: str
    language: str
    size: int
    lines: int

@dataclass
class Symbol:
    name: str
    type: str
    line: int
    context: str


def index_project(root_dir: str = ".") -> CodebaseIndexer:
    """Index a project for context-aware AI."""
    return CodebaseIndexer(root_dir)
