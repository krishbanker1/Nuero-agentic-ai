# CINEMATIC DESIGN INTELLIGENCE SYSTEM v3.1

Create a skill file at: `neuro/skills/cinematic_design.py`

**Purpose:** Analyzes ANY visual content and autonomously detects which technology stack (GSAP, Three.js, Framer Motion, etc.) to use, then generates the complete implementation.

---

## CORE PHILOSOPHY

1. **NO HARDCODED PLATFORMS** - Handles ANY URL format
2. **NO HARDCODED VALUES** - All metrics derived from actual content
3. **NO REFERENCE WEBSITES** - Generic methodology
4. **AUTONOMOUS TECH DETECTION** - Detects which animation/3D library to use

---

## TECHNOLOGY STACK DETECTION

### Method: _detect_technology_stack(frame: np.ndarray, motion_level: str, depth_perception: str) -> Dict

The system must detect which technologies are needed:

```python
TECHNOLOGY_STACKS = {
    "animation_libraries": ["gsap", "framer_motion", "css_animation", "react-spring", "motion_one"],
    "3d_libraries": ["threejs", "react-three-fiber", "css_3d", "babylonjs"],
    "text_animation": ["split_type", "blotter", "textillate", "css_text"],
    "scroll_libraries": ["lenis", "locomotive_scroll", "gsap_scroll", "native_scroll"],
}
```

### Detection Logic:

```python
def _detect_technology_stack(self, frame: np.ndarray, motion_level: str, 
                             depth_perception: str, brightness_level: str) -> Dict:
    """
    Detect which technology stack is needed based on visual analysis.
    """
    technology_stack = {
        "animation_library": None,
        "3d_library": None,
        "text_animation": None,
        "scroll_effect": None,
        "recommended_packages": [],
        "reasoning": {}
    }
    
    # === STEP 1: Detect ANIMATION LIBRARY ===
    
    # Heavy motion + dark theme = GSAP (most powerful)
    if motion_level == "heavy" and brightness_level == "dark":
        technology_stack["animation_library"] = "gsap"
        technology_stack["recommended_packages"].append("gsap")
        technology_stack["reasoning"]["animation"] = "Heavy motion detected + dark theme → GSAP (best for complex timelines)"
    
    # React project + smooth motion = Framer Motion
    elif motion_level in ["subtle", "static"] and brightness_level != "dark":
        technology_stack["animation_library"] = "framer_motion"
        technology_stack["recommended_packages"].append("framer-motion")
        technology_stack["reasoning"]["animation"] = "Subtle motion + React → Framer Motion (React-native friendly)"
    
    # High frequency motion (looping, oscillating) = GSAP
    elif motion_level == "heavy":
        technology_stack["animation_library"] = "gsap"
        technology_stack["recommended_packages"].append("gsap")
        technology_stack["reasoning"]["animation"] = "High motion complexity → GSAP (best timeline control)"
    
    # Simple fade/slide = CSS Animation
    else:
        technology_stack["animation_library"] = "css_animation"
        technology_stack["reasoning"]["animation"] = "Minimal motion → CSS Animation (no dependencies)"
    
    # === STEP 2: Detect 3D LIBRARY ===
    
    # High edge score = 3D content
    if depth_perception == "3d":
        # Check if real 3D (high contrast edges) or simulated (gradient-based)
        edge_variance = self._detect_edge_variance(frame)
        
        if edge_variance > 0.3:
            # Real 3D product/object rotation
            technology_stack["3d_library"] = "threejs"
            technology_stack["recommended_packages"].extend(["three", "@react-three/fiber", "@react-three/drei"])
            technology_stack["reasoning"]["3d"] = f"Real 3D depth (edge_variance={edge_variance:.2f}) → Three.js/R3F"
        else:
            # Simulated 3D with CSS
            technology_stack["3d_library"] = "css_3d"
            technology_stack["reasoning"]["3d"] = f"Simulated 3D (edge_variance={edge_variance:.2f}) → CSS 3D transforms"
    
    elif depth_perception == "2.5d":
        # Layered parallax effect
        technology_stack["3d_library"] = "css_3d"
        technology_stack["reasoning"]["3d"] = "2.5D depth → CSS parallax layers"
    
    # === STEP 3: Detect TEXT ANIMATION ===
    
    # Dark cinematic = SplitType for character animations
    if brightness_level == "dark":
        technology_stack["text_animation"] = "split_type"
        technology_stack["recommended_packages"].append("split-type")
        technology_stack["reasoning"]["text"] = "Dark cinematic → SplitType for letter-by-letter reveals"
    
    # Any hero section = character/word animation likely needed
    elif motion_level != "static":
        technology_stack["text_animation"] = "split_type"
        technology_stack["recommended_packages"].append("split-type")
        technology_stack["reasoning"]["text"] = "Animated hero → SplitType for staggered text"
    
    # === STEP 4: Detect SCROLL EFFECTS ===
    
    # Scene changes indicate scroll-triggered animations
    if hasattr(self, 'scene_changes') and self.scene_changes > 3:
        technology_stack["scroll_effect"] = "lenis"
        technology_stack["recommended_packages"].append("lenis")
        technology_stack["reasoning"]["scroll"] = f"{self.scene_changes} scene changes → Lenis smooth scroll"
    
    return technology_stack
```

### Helper: Edge Variance Detection

```python
def _detect_edge_variance(self, frame: np.ndarray) -> float:
    """
    Detect if edges are real 3D (high variance = sharp shadows/occlusion)
    or simulated (low variance = smooth gradients).
    """
    gray = np.mean(frame, axis=2)
    
    # Sobel edge detection
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    
    # Variance of edge magnitudes indicates real 3D vs flat
    variance = np.var(sobel_magnitude)
    normalized_variance = variance / (np.mean(sobel_magnitude) + 1e-10)
    
    return normalized_variance
```

---

## TECHNOLOGY SELECTION MATRIX

| Visual Pattern | Animation | 3D | Text | Scroll |
|----------------|-----------|-----|------|--------|
| Dark + Heavy Motion + Real 3D | GSAP | Three.js | SplitType | Lenis |
| Light + Subtle Motion + CSS 3D | Framer Motion | CSS 3D | CSS | Native |
| Cinematic Hero + Product Rotate | GSAP | Three.js | SplitType | Lenis |
| Minimal + Flat + Fast Load | CSS | None | CSS | Native |
| Parallax Layers | GSAP Scroll | CSS 3D | SplitType | Lenis |
| Text-heavy Reveal | GSAP | None | SplitType | Native |

---

## GENERATE_ANIMATION_CSS(method: str, params: Dict, stack: Dict) -> str

### Purpose:
Generate animation code based on DETECTED technology stack.

```python
def generate_animation_css(self, params: Dict, stack: Dict) -> Dict:
    """
    Generate animation CSS/JS based on detected technology.
    Returns dict with code for each technology in the stack.
    """
    animation_library = stack.get("animation_library", "css_animation")
    3d_library = stack.get("3d_library", None)
    text_animation = stack.get("text_animation", None)
    
    result = {
        "animation_code": None,
        "3d_code": None,
        "text_code": None,
        "imports": [],
        "technology_used": []
    }
    
    # Generate based on detected technologies
    if animation_library == "gsap":
        result["animation_code"] = self._generate_gsap_animation(params)
        result["imports"].append("import { gsap } from 'gsap'")
        result["imports"].append("import { ScrollTrigger } from 'gsap/ScrollTrigger'")
        result["technology_used"].append("GSAP")
    
    elif animation_library == "framer_motion":
        result["animation_code"] = self._generate_framer_motion(params)
        result["imports"].append("import { motion } from 'framer-motion'")
        result["technology_used"].append("Framer Motion")
    
    elif animation_library == "css_animation":
        result["animation_code"] = self._generate_css_keyframes(params)
        result["technology_used"].append("CSS Animation")
    
    if 3d_library == "threejs":
        result["3d_code"] = self._generate_threejs_component(params)
        result["imports"].extend([
            "import * as THREE from 'three'",
            "import { Canvas } from '@react-three/fiber'",
            "import { OrbitControls, Environment } from '@react-three/drei'"
        ])
        result["technology_used"].append("Three.js/R3F")
    
    elif 3d_library == "css_3d":
        result["3d_code"] = self._generate_css_3d(params)
        result["technology_used"].append("CSS 3D")
    
    if text_animation == "split_type":
        result["text_code"] = self._generate_splittext_animation(params)
        result["imports"].append("import SplitType from 'split-type'")
        result["technology_used"].append("SplitType")
    
    return result
```

---

## _generate_gsap_animation(params: Dict) -> str

```python
def _generate_gsap_animation(self, params: Dict) -> str:
    """
    Generate GSAP animation code.
    GSAP is chosen when: heavy motion OR dark cinematic OR complex timelines
    """
    motion_level = params.get("motion_level", "subtle")
    
    if motion_level == "heavy":
        stagger = 0.05
        duration = 0.8
        ease = "expo.out"
    else:
        stagger = 0.15
        duration = 0.6
        ease = "power3.out"
    
    return f"""
// GSAP Animation - Auto-generated based on motion_level: {motion_level}
import {{ gsap }} from 'gsap'
import {{ ScrollTrigger }} from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useGSAPAnimation() {{
  // Hero entrance timeline
  const heroTimeline = gsap.timeline()

  // Navbar - slide from top
  heroTimeline.from('.navbar', {{
    y: -100,
    opacity: 0,
    duration: 0.8,
    ease: '{ease}'
  }}, 0)

  // Title - fade up with stagger
  heroTimeline.from('.hero-title span', {{
    y: 100,
    opacity: 0,
    stagger: {stagger},
    duration: {duration},
    ease: '{ease}'
  }}, 0.2)

  // Subtitle - fade up
  heroTimeline.from('.hero-subtitle', {{
    y: 50,
    opacity: 0,
    duration: {duration * 0.8},
    ease: '{ease}'
  }}, 0.4)

  // CTA button - scale in
  heroTimeline.from('.hero-cta', {{
    scale: 0.8,
    opacity: 0,
    duration: 0.5,
    ease: 'back.out(1.7)'
  }}, 0.6)

  // Scroll indicator - bounce
  gsap.to('.scroll-indicator', {{
    y: 10,
    duration: 1,
    repeat: -1,
    yoyo: true,
    ease: 'power1.inOut'
  }})

  // Scroll-triggered reveal for sections
  gsap.utils.toArray('.reveal-section').forEach((section) => {{
    gsap.from(section, {{
      y: 100,
      opacity: 0,
      duration: 1,
      scrollTrigger: {{
        trigger: section,
        start: 'top 80%',
        toggleActions: 'play none none reverse'
      }}
    }})
  }})
}}
"""
```

---

## _generate_threejs_component(params: Dict) -> str

```python
def _generate_threejs_component(self, params: Dict) -> str:
    """
    Generate Three.js/R3F component.
    Chosen when: depth_perception == '3d' AND high edge variance
    """
    lighting_type = params.get("lighting_type", "ambient")
    
    if lighting_type == "spotlight":
        lights_config = """
        <spotLight 
          position={[10, 10, 10]} 
          angle={0.15} 
          penumbra={1}
          intensity={1}
          color="#ffffff"
        />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        """
    else:
        lights_config = """
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        """
    
    return f"""
// Three.js/R3F Component - Auto-generated
import {{ Canvas }} from '@react-three/fiber'
import {{ OrbitControls, Environment, Float, MeshDistortMaterial }} from '@react-three/drei'

export function ThreeScene() {{
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
      {lights_config}
      
      {/* Main 3D Element with distortion */}
      <Float speed={{2}} rotationIntensity={{1}} floatIntensity={{1}}>
        <mesh>
          <sphereGeometry args={{[1, 64, 64]}} />
          <MeshDistortMaterial 
            color="#8a2be2"
            distort={{0.4}}
            speed={{2}}
            roughness={{0.1}}
            metalness={{0.8}}
          />
        </mesh>
      </Float>
      
      {/* Background particles */}
      <Particles count={{100}} />
      
      <OrbitControls enableZoom={{false}} autoRotate autoRotateSpeed={{0.5}} />
    </Canvas>
  )
}}

function Particles({{ count }}) {{
  const positions = new Float32Array(count * 3)
  for (let i = 0; i < count; i++) {{
    positions[i * 3] = (Math.random() - 0.5) * 10
    positions[i * 3 + 1] = (Math.random() - 0.5) * 10
    positions[i * 3 + 2] = (Math.random() - 0.5) * 10
  }}
  
  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={{count}}
          array={{positions}}
          itemSize={{3}}
        />
      </bufferGeometry>
      <pointsMaterial size={{0.02}} color="#8a2be2" transparent opacity={{0.6}} />
    </points>
  )
}}
"""
```

---

## _generate_splittext_animation(params: Dict) -> str

```python
def _generate_splittext_animation(self, params: Dict) -> str:
    """
    Generate SplitType text animation.
    Chosen when: dark theme OR animated hero sections
    """
    motion_level = params.get("motion_level", "subtle")
    
    if motion_level == "heavy":
        stagger = 0.03
        duration = 0.8
        from_y = 80
    else:
        stagger = 0.08
        duration = 0.6
        from_y = 50
    
    return f"""
// SplitType Text Animation - Auto-generated
import {{ useEffect, useRef }} from 'react'
import SplitType from 'split-type'
import {{ gsap }} from 'gsap'

export function AnimatedText({{ text, className }}) {{
  const textRef = useRef(null)
  const splitRef = useRef(null)

  useEffect(() => {{
    if (!textRef.current) return

    // Split text into characters
    const split = new SplitType(textRef.current, {{
      types: 'chars, words',
      tagClass: 'split-text'
    }})

    splitRef.current = split

    // Animate characters
    gsap.from(split.chars, {{
      y: {from_y},
      opacity: 0,
      rotateX: -90,
      stagger: {stagger},
      duration: {duration},
      ease: 'power3.out',
      delay: 0.2
    }})

    // Cleanup
    return () => split.revert()
  }}, [text])

  return (
    <div ref={{textRef}} className={{className}}>
      {{text}}
    </div>
  )
}}
"""
```

---

## _generate_css_3d(params: Dict) -> str

```python
def _generate_css_3d(self, params: Dict) -> str:
    """
    Generate CSS 3D transforms.
    Chosen when: 2.5D depth OR low edge variance (simulated 3D)
    """
    edge_score = params.get("edge_score", 100)
    depth = min(edge_score / 50, 5)  # Scale depth with edge score
    
    return f"""
/* CSS 3D Transforms - Auto-generated */
/* depth_perception: 2.5D, edge_score: {edge_score} */

.scene-3d {{
  transform-style: preserve-3d;
  perspective: 1000px;
}}

.layer {{
  transform-style: preserve-3d;
  backface-visibility: hidden;
}}

/* Parallax layers based on depth */
.parallax-layer-1 {{ transform: translateZ({depth}px) scale(1.1); }}
.parallax-layer-2 {{ transform: translateZ({depth * 0.7}px) scale(1.05); }}
.parallax-layer-3 {{ transform: translateZ({depth * 0.4}px) scale(1.02); }}
.parallax-layer-bg {{ transform: translateZ(-{depth}px) scale(1.2); }}

/* 3D card flip */
.card-3d {{
  transform-style: preserve-3d;
  transition: transform 0.8s;
  cursor: pointer;
}}

.card-3d:hover {{
  transform: rotateY(180deg);
}}

.card-front, .card-back {{
  position: absolute;
  backface-visibility: hidden;
}}

.card-back {{
  transform: rotateY(180deg);
}}
"""
```

---

## _generate_css_keyframes(params: Dict) -> str

```python
def _generate_css_keyframes(self, params: Dict) -> str:
    """
    Generate CSS keyframe animations.
    Chosen when: minimal motion OR no special requirements
    """
    motion_level = params.get("motion_level", "subtle")
    
    if motion_level == "heavy":
        slide_distance = 60
        duration = 0.5
    else:
        slide_distance = 40
        duration = 0.7
    
    return f"""
/* CSS Keyframe Animations - Auto-generated */
/* motion_level: {motion_level} */

@keyframes fade-up {{
  from {{
    opacity: 0;
    transform: translateY({slide_distance}px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes fade-in {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}

@keyframes scale-in {{
  from {{
    opacity: 0;
    transform: scale(0.9);
  }}
  to {{
    opacity: 1;
    transform: scale(1);
  }}
}}

/* Stagger animation for children */
.stagger-animation > * {{
  animation: fade-up {duration}s ease-out forwards;
  opacity: 0;
}}

.stagger-animation > *:nth-child(1) {{ animation-delay: 0s; }}
.stagger-animation > *:nth-child(2) {{ animation-delay: {duration * 0.3}s; }}
.stagger-animation > *:nth-child(3) {{ animation-delay: {duration * 0.6}s; }}
.stagger-animation > *:nth-child(4) {{ animation-delay: {duration * 0.9}s; }}
.stagger-animation > *:nth-child(5) {{ animation-delay: {duration * 1.2}s; }}
"""
```

---

## COMPLETE BUILD FLOW

```
build_from_input(input_data)
    ↓
analyze_input() → extracts brightness, edge_score, motion_level, depth_perception
    ↓
_detect_technology_stack() → decides: GSAP vs Framer Motion, Three.js vs CSS 3D, etc.
    ↓
generate_animation_css() → generates code for EACH detected technology
    ↓
generate_complete_component() → combines all code + stacks into final output
    ↓
{
    "technology_stack": {...},     # What was detected and why
    "animation_code": "...",      # GSAP or Framer Motion or CSS
    "3d_code": "...",             # Three.js or CSS 3D or None
    "text_code": "...",           # SplitType or CSS
    "recommended_packages": [...], # What to install
    "css": "...",
    "jsx": "...",
}
```

---

## TECHNOLOGY DETECTION RULES (Summary)

| Condition | Animation | 3D | Text | Scroll |
|-----------|-----------|-----|------|--------|
| edge_score > 200 + high variance | GSAP | Three.js | SplitType | Lenis |
| motion_level=heavy + dark | GSAP | Three.js | SplitType | Lenis |
| motion_level=subtle + light | Framer Motion | CSS 3D | CSS | Native |
| edge_score < 50 (flat) | CSS | None | CSS | Native |
| 2.5D depth | GSAP | CSS 3D | SplitType | Lenis |

---

## TECHNICAL REQUIREMENTS

```bash
# Core analysis packages
pip install yt-dlp opencv-python Pillow numpy requests

# Animation packages (based on detection, install what you need)
npm install gsap framer-motion split-type

# 3D packages (if needed)
npm install three @react-three/fiber @react-three/drei

# Scroll packages (if needed)
npm install lenis
```

---

## EXAMPLE OUTPUT

```python
result = design.build_from_input("https://instagram.com/reel/abc123")
print(result["technology_stack"])
# {
#     "animation_library": "gsap",
#     "3d_library": "threejs",
#     "text_animation": "split_type",
#     "scroll_effect": "lenis",
#     "recommended_packages": ["gsap", "three", "@react-three/fiber", "@react-three/drei", "split-type", "lenis"],
#     "reasoning": {
#         "animation": "Heavy motion detected + dark theme → GSAP",
#         "3d": "Real 3D depth (edge_variance=0.45) → Three.js/R3F",
#         "text": "Dark cinematic → SplitType",
#         "scroll": "5 scene changes → Lenis"
#     }
# }
```

---

END OF SYSTEM v3.1
