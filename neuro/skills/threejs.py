"""Three.js - 3D WebGL using REAL AI"""
from neuro.router.smart_router import SmartRouter

class ThreeJS:
    """Generate Three.js scenes using REAL AI."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def generate_scene(self, description: str) -> str:
        """Generate Three.js scene using REAL AI."""
        prompt = f"""Generate Three.js 3D scene for: {description}

Include:
- Scene, camera, renderer setup
- Geometry (Box, Sphere, etc)
- Material and lighting
- Animation loop
- OrbitControls for interaction
- Mouse/touch handling

Output as complete HTML with embedded Three.js. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_ui")
    
    def generate_particles(self, count: int = 5000) -> str:
        """Generate particle system."""
        prompt = f"""Generate Three.js particle system with {count} particles.

Include:
- Points geometry
- PointsMaterial with custom shader
- Mouse interaction
- Slow rotation
- Performance optimization

Output as complete HTML. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_ui")
    
    def generate_model_loader(self, format: str = "glb") -> str:
        """Generate 3D model loader."""
        prompt = """Generate Three.js GLTF/GLB model loader with:
- GLTFLoader
- OrbitControls
- Loading animation
- Error handling

Output as complete HTML. No markdown.
"""
        return self.router.chat(prompt, task_type="frontend_ui")


def threejs_scene(description: str) -> str:
    """Quick Three.js scene generator."""
    return ThreeJS().generate_scene(description)
