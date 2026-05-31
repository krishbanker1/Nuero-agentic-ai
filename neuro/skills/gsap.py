"""GSAP - Animations using REAL AI"""
from neuro.router.smart_router import SmartRouter

class GSAP:
    """Generate GSAP animations using REAL AI."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def generate_animations(self, description: str) -> str:
        """Generate GSAP animations using REAL AI."""
        prompt = f"""Generate GSAP animations for: {description}
Include:
- gsap.to() and gsap.from() animations
- Timeline for sequenced animations
- ScrollTrigger for scroll-based animations
- Stagger effects
- Hover animations

Output as complete HTML with embedded GSAP. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_ui")
    
    def generate_scroll_animations(self) -> str:
        """Generate scroll-triggered animations."""
        prompt = """Generate GSAP ScrollTrigger animations including:
- Section reveals
- Parallax effects
- Progress indicators
- Sticky elements

Output as complete HTML. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_ui")


def gsap_animation(description: str) -> str:
    """Quick GSAP animation generator."""
    return GSAP().generate_animations(description)
