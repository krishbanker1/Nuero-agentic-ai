"""Planning & Task Breakdown - Break work into ordered tasks using REAL AI"""
from typing import Dict, Any, List
from neuro.router.smart_router import SmartRouter

class PlanningTaskBreakdown:
    """Break work into implementable tasks."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def breakdown(self, spec: str) -> Dict[str, Any]:
        """Break spec into ordered tasks."""
        
        prompt = f"""Break this task into ordered, implementable tasks:

TASK: {spec}

Create a task breakdown with:
1. Phases (ordered)
2. Each phase has 3-5 specific tasks
3. Dependencies between tasks
4. Estimated complexity (small/medium/large)
5. Tasks that can run parallel

Format:
## Phase 1: [Name]
- [ ] Task 1.1: [specific action]
- [ ] Task 1.2: [specific action]

## Phase 2: [Name] (depends on Phase 1)
...
"""
        
        result = self.router.chat(prompt, task_type="reasoning_planning")
        
        return {
            "spec": spec,
            "breakdown": result,
            "format": "markdown_task_list"
        }
    
    def estimate_effort(self, tasks: List[str]) -> str:
        """Estimate effort for tasks."""
        prompt = f"""Estimate effort for these tasks:

TASKS:
{chr(10).join('- ' + t for t in tasks)}

For each task estimate:
- Time: minutes/hours/days
- Complexity: low/medium/high
- Risk: low/medium/high

Output estimate.
"""
        return self.router.chat(prompt, task_type="reasoning_planning")


def plan_tasks(spec: str) -> Dict[str, Any]:
    """Quick task planning."""
    return PlanningTaskBreakdown().breakdown(spec)
