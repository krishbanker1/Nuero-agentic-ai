"""
Neuro Studio - Web UI for Neuro Autonomous Agent

Provides a browser-based interface for:
- Prompt composition
- Image/screenshot upload
- Provider health display
- Working directory selection
- App preview launching
- Live agent status

Usage: python -m neuro --ui [--ui-host 127.0.0.1] [--ui-port 8765] [--no-open-browser]
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

# Templates directory
TEMPLATE_DIR = Path(__file__).parent / "templates"


def get_available_providers() -> dict[str, int]:
    """Get count of available API keys per provider."""
    providers = {}
    provider_vars = {
        "groq": ["GROQ_API_KEYS", "GROQ_API_KEY"],
        "google": ["GEMINI_API_KEYS", "GEMINI_API_KEY"],
        "openrouter": ["OPENROUTER_API_KEYS", "OPENROUTER_API_KEY"],
        "huggingface": ["HF_TOKEN", "HUGGINGFACE_API_KEYS", "HUGGINGFACE_API_KEY"],
        "cloudflare": ["CLOUDFLARE_AI_API_TOKEN", "CLOUDFLARE_API_KEY"],
        "together": ["TOGETHER_API_KEYS", "TOGETHER_API_KEY"],
    }

    for provider, vars in provider_vars.items():
        count = sum(1 for v in vars if os.getenv(v))
        if count > 0:
            providers[provider] = count

    return providers


def run_neuro_goal(goal: str, working_dir: str = ".", dry_run: bool = False,
                   max_steps: int = 50, max_passes: int = 4,
                   screenshots: list[str] | None = None) -> dict[str, Any]:
    """Run Neuro agent with the given goal."""
    try:
        import re

        from neuro.executor.agent_loop import create_agent

        # Prepend screenshot references to goal
        if screenshots:
            screenshot_note = "\n\nScreenshots uploaded for reference:\n"
            for path in screenshots:
                screenshot_note += f"- {path}\n"
            goal = goal + screenshot_note

        # Create project folder with slug from goal
        repo_root = Path(__file__).parent.parent
        builds_dir = repo_root / "neuro-build-apps"
        builds_dir.mkdir(exist_ok=True)

        # Create folder name from goal (sanitize)
        goal_slug = re.sub(r'[^a-zA-Z0-9]', '-', goal.lower())[:50]
        goal_slug = re.sub(r'-+', '-', goal_slug).strip('-')
        project_dir = builds_dir / goal_slug

        # Handle duplicate folder names
        counter = 1
        while project_dir.exists():
            project_dir = builds_dir / f"{goal_slug}-{counter}"
            counter += 1

        project_dir.mkdir(parents=True, exist_ok=True)
        abs_working_dir = str(project_dir)

        agent = create_agent(
            goal=goal,
            working_dir=abs_working_dir,
            max_steps=max_steps,
            max_passes=max_passes,
            dry_run=dry_run,
            verbose=True,
        )

        result = agent.run()

        # List files created for debugging
        workspace_path = Path(abs_working_dir)
        created_files = []
        if workspace_path.exists():
            for f in workspace_path.rglob("*"):
                if f.is_file() and f.suffix in ['.html', '.py', '.js', '.css', '.json']:
                    created_files.append(str(f.relative_to(workspace_path)))

        return {
            "success": result.success,
            "status": result.status,
            "steps": result.steps,
            "passes_used": result.passes_used,
            "duration_ms": result.duration_ms,
            "files_changed": result.files_changed or [],
            "files_created": created_files[:20],
            "working_dir": abs_working_dir,
            "project_folder": str(project_dir.relative_to(repo_root)),
            "validation_passed": result.validation_passed,
            "error": result.error,
            "output": _capture_output(result),
        }
    except Exception as e:
        error_str = str(e)
        if "api" in error_str.lower() or "key" in error_str.lower():
            error_str = "API provider error - check your API keys"

        return {
            "success": False,
            "status": "error",
            "error": error_str,
            "output": f"Exception: {type(e).__name__}",
        }


def _capture_output(result) -> str:
    """Capture agent output as string."""
    output_parts = []
    if result.steps:
        output_parts.append(f"Steps completed: {result.steps}")
    if result.files_changed:
        output_parts.append(f"Files changed: {', '.join(result.files_changed[:10])}")
        if len(result.files_changed) > 10:
            output_parts.append(f"... and {len(result.files_changed) - 10} more")
    if result.error:
        output_parts.append(f"Error: {result.error}")
    return "\n".join(output_parts) if output_parts else "Completed successfully"


# App preview management
_preview_processes: dict[str, subprocess.Popen] = {}
_preview_lock = threading.RLock()


def launch_app_preview(workspace: str = None, request_host: str = "127.0.0.1:8080",
                        port: int = 8080, app_type: str = "auto") -> dict[str, Any]:
    """Launch a preview server for the generated app."""

    # If no workspace provided, look in neuro-build-apps
    if not workspace:
        repo_root = Path(__file__).parent.parent
        builds_dir = repo_root / "neuro-build-apps"

        if builds_dir.exists():
            # Get the most recently modified folder
            folders = [f for f in builds_dir.iterdir() if f.is_dir()]
            if folders:
                # Sort by modification time, newest first
                folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                workspace = str(folders[0])

    if not workspace:
        return {"success": False, "error": "No workspace found. Build an app first!"}

    workspace_path = Path(workspace)

    if not workspace_path.exists():
        return {"success": False, "error": f"Workspace does not exist: {workspace}"}

    with _preview_lock:
        stop_app_previews()

        try:
            entry_point = None

            # Look for index.html
            for possible_index in [
                workspace_path / "index.html",
                workspace_path / "templates" / "index.html",
                workspace_path / "public" / "index.html",
                workspace_path / "dist" / "index.html",
                workspace_path / "build" / "index.html",
            ]:
                if possible_index.exists():
                    entry_point = possible_index
                    break

            python_entry = None
            if (workspace_path / "app.py").exists():
                python_entry = workspace_path / "app.py"
            elif (workspace_path / "server.py").exists():
                python_entry = workspace_path / "server.py"
            elif (workspace_path / "main.py").exists():
                python_entry = workspace_path / "main.py"

            if python_entry and (workspace_path / "requirements.txt").exists():
                if (workspace_path / "app.py").exists():
                    cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", str(port)]
                elif (workspace_path / "server.py").exists():
                    cmd = [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", str(port)]
                else:
                    cmd = [sys.executable, str(python_entry)]

                preview = subprocess.Popen(cmd, cwd=str(workspace_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                app_type = "python"
            elif entry_point:
                cmd = [sys.executable, "-m", "http.server", str(port)]
                preview = subprocess.Popen(cmd, cwd=str(workspace_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                app_type = "static"
            else:
                files = [str(f.relative_to(workspace_path)) for f in workspace_path.rglob("*") if f.is_file()]
                return {"success": False, "error": "No entry point found", "files": files[:20], "workspace": str(workspace_path)}

            time.sleep(2)

            if preview.poll() is not None:
                return {"success": False, "error": "Server failed to start", "app_type": app_type}

            _preview_processes[str(port)] = preview

            host_part = request_host.split(":")[0]
            browser_url = f"http://{host_part}:{port}"

            return {
                "success": True,
                "browser_url": browser_url,
                "app_type": app_type,
                "port": port,
                "entry_point": str(entry_point) if entry_point else str(python_entry) if python_entry else None,
                "workspace": str(workspace_path),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def stop_app_previews() -> None:
    """Stop all preview servers."""
    with _preview_lock:
        for _port, proc in list(_preview_processes.items()):
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        _preview_processes.clear()


def sanitize_filename(filename: str) -> str:
    """Sanitize upload filename to prevent path traversal."""
    filename = os.path.basename(filename)
    # Replace path separators and dangerous patterns
    filename = filename.replace("\\", "_").replace("/", "_")
    # Replace multiple dots (like "..") but keep single dots for extensions
    while ".." in filename:
        filename = filename.replace("..", "_")
    filename = re.sub(r"[^\w\s.-]", "_", filename)
    return filename[:100]


def save_uploaded_file(content: bytes, filename: str, upload_dir: Path) -> str:
    """Save uploaded file with sanitized name."""
    filename = sanitize_filename(filename)

    timestamp = int(time.time() * 1000)
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        safe_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
    else:
        safe_name = f"{filename}_{timestamp}"

    filepath = upload_dir / safe_name

    # Cap file size at 10MB
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("File too large (max 10MB)")

    filepath.write_bytes(content)
    return str(filepath.relative_to(Path.cwd()))


def get_studio_html() -> str:
    """Get the Neuro Studio HTML template from file."""
    template_path = TEMPLATE_DIR / "studio.html"

    if template_path.exists():
        return template_path.read_text()

    # Fallback minimal HTML
    return """<!DOCTYPE html>
<html><head><title>Neuro Studio</title></head>
<body><h1>Neuro Studio</h1>
<p>Template not found. Please reinstall.</p></body></html>"""


class StudioHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Neuro Studio."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(get_studio_html().encode())

        elif parsed.path == "/api/health":
            providers = get_available_providers()
            health_data = {"providers": {}, "timestamp": time.time()}

            for name, count in providers.items():
                health_data["providers"][name] = {"count": count, "status": "healthy"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                # Handle potential decode errors
                try:
                    body_str = body.decode('utf-8')
                except UnicodeDecodeError:
                    body_str = body.decode('utf-8', errors='replace')

                data = json.loads(body_str)
                goal = data.get("goal", "")
                working_dir = data.get("working_dir", ".")
                dry_run = data.get("dry_run", False)
                max_steps = data.get("max_steps", 50)
                screenshots = data.get("screenshots", [])

                result = run_neuro_goal(
                    goal=goal,
                    working_dir=working_dir,
                    dry_run=dry_run,
                    max_steps=max_steps,
                    screenshots=screenshots
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "status": "error",
                    "error": "Invalid JSON request",
                    "output": ""
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "status": "error",
                    "error": str(e),
                    "output": f"Exception: {type(e).__name__}"
                }).encode())

        elif parsed.path == "/api/upload":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            upload_dir = Path(".neuro_uploads")
            upload_dir.mkdir(exist_ok=True)

            try:
                filename = "upload.png"
                filepath = save_uploaded_file(body[:10*1024*1024], filename, upload_dir)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "path": filepath}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif parsed.path == "/api/launch" or parsed.path == "/api/preview":
            parsed_qs = parse_qs(parsed.query)
            workspace = parsed_qs.get("workspace", [None])[0]
            request_host = self.headers.get("Host", "127.0.0.1:8080")

            # Pass None to let launch_app_preview find the latest build
            result = launch_app_preview(workspace, request_host, port=8080)

            self.send_response(200 if result.get("success") else 400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        elif parsed.path == "/api/stop":
            stop_app_previews()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        else:
            self.send_response(404)
            self.end_headers()


def start_studio(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True):
    """Start the Neuro Studio web server."""
    server = HTTPServer((host, port), StudioHandler)

    url = f"http://{host}:{port}"
    print(f"\nNeuro Studio running at {url}")
    print("   Press Ctrl+C to stop\n")

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Neuro Studio...")
        stop_app_previews()
        server.shutdown()


if __name__ == "__main__":
    start_studio()
