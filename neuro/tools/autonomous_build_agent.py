"""Autonomous Build Agent - Build, test, fix, screenshot loop using REAL AI"""
from typing import Dict, Any
from neuro.router.smart_router import SmartRouter
from neuro.tools.browser_automation import BrowserAutomation
from neuro.tools.terminal_executor import TerminalExecutor

class AutonomousBuildAgent:
    """
    Complete autonomous agent like OpenHands:
    1. Browse/research websites
    2. Build apps with code generation
    3. Test and run commands
    4. Find and fix errors
    5. Take screenshots of results
    
    All 100% FREE - no paid services.
    """
    
    def __init__(self):
        self.router = SmartRouter()
        self.browser = BrowserAutomation()
        self.terminal = TerminalExecutor()
    
    def run(self, task: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Run autonomous task loop."""
        
        history = []
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Step 1: Think (use AI)
            thought = self._think(task, iteration, history)
            history.append({"role": "assistant", "content": thought})
            
            # Step 2: Execute based on thought
            if "browse" in thought.lower():
                result = self._browse(thought)
            elif "build" in thought.lower() or "generate" in thought.lower():
                result = self._build(thought)
            elif "test" in thought.lower() or "run" in thought.lower():
                result = self._test_and_fix(thought)
            elif "screenshot" in thought.lower() or "verify" in thought.lower():
                result = self._verify_and_screenshot(thought)
            else:
                result = self._execute_command(thought)
            
            history.append({"role": "tool", "content": result})
            
            # Check if done
            if self._is_complete(result, history):
                break
        
        return {
            "task": task,
            "iterations": iteration,
            "history": history,
            "final_state": history[-1] if history else None
        }
    
    def _think(self, task: str, iteration: int, history: list) -> str:
        """Use AI to decide next action."""
        
        history_str = "\n".join([f"{h['role']}: {h['content'][:200]}..." for h in history[-3:]])
        
        prompt = f"""You are an autonomous agent. Decide the next action.

TASK: {task}
ITERATION: {iteration}/10
RECENT HISTORY:
{history_str}

Choose ONE action:
- browse: Visit websites to gather info
- build: Generate code/UI using skills
- test: Run commands to test/build
- fix: Fix errors found
- screenshot: Take screenshot to verify
- done: Task is complete

Respond with action and details.
"""
        
        return self.router.chat(prompt, task_type="reasoning_planning")
    
    def _browse(self, thought: str) -> Dict[str, Any]:
        """Browse websites."""
        # Extract URL from thought
        import re
        urls = re.findall(r'https?://[^\s]+', thought)
        
        if urls:
            self.browser.start()
            result = self.browser.navigate(urls[0])
            self.browser.screenshot("browse_result.png")
            self.browser.close()
            return {"action": "browse", "result": result}
        
        return {"action": "browse", "result": "No URL found"}
    
    def _build(self, thought: str) -> Dict[str, Any]:
        """Build using skills."""
        # Extract what to build
        prompt = f"""Extract what to build from this thought: {thought}

Respond with brief description of the app/feature to build.
"""
        
        spec = self.router.chat(prompt, task_type="reasoning_planning")
        
        # Use appropriate skill based on spec
        if "website" in spec.lower() or "landing" in spec.lower():
            from neuro.skills.website_builder import build_website
            result = build_website(spec)
        elif "app" in spec.lower() or "full-stack" in spec.lower():
            from neuro.skills.frontend_builder import build_frontend
            result = build_frontend(spec)
        elif "api" in spec.lower():
            from neuro.skills.rest_api_builder import build_rest_api
            result = build_rest_api(spec)
        else:
            from neuro.skills.code_generator import quick_generate
            result = {"code": quick_generate(spec)}
        
        return {"action": "build", "result": result}
    
    def _test_and_fix(self, thought: str) -> Dict[str, Any]:
        """Run commands and fix errors."""
        # Extract command
        import re
        commands = re.findall(r'`([^`]+)`', thought)
        
        if not commands:
            # Generate command based on what needs testing
            prompt = f"""What command would you run to test/deploy this? {thought}
Only output the command, nothing else."""
            cmd_text = self.router.chat(prompt, task_type="reasoning_planning")
            commands = re.findall(r'`([^`]+)`', cmd_text)
        
        if commands:
            result = self.terminal.run(commands[0])
            
            # If error, use AI to fix
            if result.get("exit_code", 0) != 0:
                fix_prompt = f"""Fix this error:

COMMAND: {commands[0]}
ERROR: {result.get('stderr', result.get('error', 'Unknown error'))}

Output the FIXED command.
"""
                fixed_cmd = self.router.chat(fix_prompt, task_type="debugging")
                fixed_commands = re.findall(r'`([^`]+)`', fixed_cmd)
                
                if fixed_commands:
                    result = self.terminal.run(fixed_commands[0])
            
            return {"action": "test", "result": result}
        
        return {"action": "test", "result": "No command found"}
    
    def _verify_and_screenshot(self, thought: str) -> Dict[str, Any]:
        """Take screenshot and verify."""
        # Check if there's a running server
        result = self.terminal.run("curl -s localhost:3000 | head -20 || curl -s localhost:8000 | head -20 || echo 'No server'")
        
        if "No server" not in result.get("output", ""):
            self.browser.start()
            self.browser.navigate("http://localhost:3000" if "3000" in result.get("output", "") else "http://localhost:8000")
            self.browser.screenshot("verification.png")
            html = self.browser.get_html()
            self.browser.close()
            return {"action": "verify", "screenshot": "verification.png", "html_preview": html[:500]}
        
        return {"action": "verify", "result": "No running server to verify"}
    
    def _execute_command(self, thought: str) -> Dict[str, Any]:
        """Execute general command."""
        import re
        commands = re.findall(r'`([^`]+)`', thought)
        
        if commands:
            return self.terminal.run(commands[0])
        
        return {"action": "execute", "result": "No command found"}
    
    def _is_complete(self, result: dict, history: list) -> bool:
        """Check if task is complete."""
        if "error" not in result.get("result", "").lower():
            prompt = f"""Based on this result, is the task complete?
RESULT: {str(result)[:300]}
HISTORY: {str(history[-3:])[:300]}

Respond YES if complete, NO if needs more work.
"""
            response = self.router.chat(prompt, task_type="reasoning_planning")
            return "yes" in response.lower() and "complete" in response.lower()
        return False
    
    def close(self):
        """Cleanup."""
        try:
            self.browser.close()
        except:
            pass


def autonomous_build(task: str, max_iterations: int = 10) -> Dict[str, Any]:
    """Run autonomous build agent."""
    agent = AutonomousBuildAgent()
    result = agent.run(task, max_iterations)
    agent.close()
    return result
