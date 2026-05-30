"""Component Driven - React using REAL AI"""
from neuro.router.smart_router import SmartRouter

class ComponentDriven:
    """Generate component-driven React using REAL AI."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def generate_component(self, name: str, props: list) -> str:
        """Generate React component."""
        prompt = f"""Generate React component: {name}
Props: {', '.join(props)}
Include:
- Props destructuring
- TypeScript types
- Default props
- PropTypes validation
- Storybook story

Output as complete React code. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_react")
    
    def generate_design_system(self) -> str:
        """Generate design system."""
        prompt = """Generate React design system with:
- Button variants
- Input components
- Card component
- Typography scale
- Color tokens
- Spacing system

Use CSS-in-JS or Tailwind.
Output as complete React code. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_react")


def component_driven(name: str, props: list) -> str:
    """Quick component generator."""
    return ComponentDriven().generate_component(name, props)
