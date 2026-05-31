"""Presentation Builder - Professional slides using real AI"""
from typing import Dict, Any
from dataclasses import dataclass
from neuro.router.smart_router import SmartRouter

@dataclass
class Slide:
    title: str
    content: str
    type: str
    animation: str

class PresentationBuilder:
    """Enterprise presentation builder using real AI."""
    MODEL = "groq/llama-3.1-8b-instant"  # Fast for quick slides
    
    def __init__(self):
        self.router = SmartRouter()
    
    def build_presentation(self, topic: str, num_slides: int = 5) -> Dict[str, Any]:
        """Build complete presentation using REAL AI."""
        
        prompt = f"""Create a professional presentation about: {topic}

Generate {num_slides} slides in HTML format with:
- Title slide
- Overview/problem statement
- Key features/points (2-3 slides)
- Benefits/solutions
- Call to action/conclusion

Each slide should have:
- Bold, attention-grabbing title
- Bullet points with key information
- Professional styling (gradient backgrounds, shadows)
- Smooth CSS animations

Output as HTML that can be opened in browser.
Navigation: Arrow keys or click to navigate.
Show slide number and progress bar.

Output ONLY the complete HTML, no markdown.
"""
        
        html = self.router.chat(prompt, task_type="frontend_ui")
        
        # Create simple slide structure as fallback
        slides = [
            Slide(title=f"About: {topic[:30]}", content="Overview", type="title", animation="fade"),
            Slide(title="Key Points", content="Details", type="content", animation="slide"),
        ]
        
        return {
            "topic": topic,
            "slides": slides,
            "html": html,
            "model_used": self.MODEL,
        }


def build_presentation(topic: str) -> Dict[str, Any]:
    """Quick presentation builder using real AI."""
    return PresentationBuilder().build_presentation(topic)
