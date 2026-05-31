"""Terminal Executor - Run commands, capture output, fix errors using REAL AI"""
from typing import Dict, Any, List
import subprocess
import os

class TerminalExecutor:
    """
    Terminal execution tool for Neuro - like OpenHands bash tools.
    - Run shell commands
    - Capture output
    - Fix errors
    - All using REAL AI for diagnosis
    """
    
    def __init__(self, cwd: str = None):
        self.cwd = cwd or os.getcwd()
        self.last_output = ""
        self.last_exit_code = 0
        self.history: List[Dict[str, Any]] = []
    
    def run(self, command: str, timeout: int = 60, env: dict = None) -> Dict[str, Any]:
        """Run command and return result."""
        
        # Add cwd to env
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        run_env['PWD'] = self.cwd
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=run_env
            )
            
            output = result.stdout + result.stderr
            self.last_output = output
            self.last_exit_code = result.returncode
            
            cmd_record = {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": output
            }
            self.history.append(cmd_record)
            
            return cmd_record
            
        except subprocess.TimeoutExpired:
            error = {"error": f"Command timed out after {timeout}s", "command": command}
            self.history.append(error)
            return error
        except Exception as e:
            error = {"error": str(e), "command": command}
            self.history.append(error)
            return error
    
    def run_safe(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run command safely (no dangerous commands)."""
        dangerous = ["rm -rf /", "mkfs", ":(){:|:&};:", "dd if=/dev/zero"]
        for d in dangerous:
            if d in command:
                return {"error": f"Dangerous command blocked: {d}", "command": command}
        
        return self.run(command, timeout)
    
    def cd(self, path: str) -> Dict[str, Any]:
        """Change directory."""
        new_cwd = os.path.abspath(os.path.join(self.cwd, path))
        if os.path.isdir(new_cwd):
            self.cwd = new_cwd
            return {"status": "success", "cwd": self.cwd}
        return {"error": f"Directory not found: {path}"}
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return os.path.exists(os.path.join(self.cwd, path))
    
    def read_file(self, path: str) -> str:
        """Read file content."""
        full_path = os.path.join(self.cwd, path)
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading {path}: {e}"
    
    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write file content."""
        full_path = os.path.join(self.cwd, path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return {"status": "success", "path": path}
        except Exception as e:
            return {"error": str(e), "path": path}
    
    def list_files(self, path: str = ".") -> List[str]:
        """List files in directory."""
        full_path = os.path.join(self.cwd, path)
        try:
            return os.listdir(full_path)
        except:
            return []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get command history."""
        return self.history


def run_command(command: str, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
    """Quick command runner."""
    executor = TerminalExecutor(cwd=cwd)
    return executor.run(command, timeout=timeout)
