# CINEMATIC DESIGN INTELLIGENCE SYSTEM v3.2

Create a skill file at: `neuro/skills/cinematic_design.py`

**Purpose:** Analyzes ANY visual content and autonomously detects which technology stack to use, then generates complete implementation for ALL major animation/3D libraries.

---

## CORE PHILOSOPHY

1. **NO HARDCODED PLATFORMS** - Handles ANY URL format
2. **NO HARDCODED VALUES** - All metrics derived from actual content
3. **NO REFERENCE WEBSITES** - Generic methodology
4. **AUTONOMOUS TECH DETECTION** - Detects which animation/3D library to use

---

## COMPLETE TECHNOLOGY STACKS

### All Supported Libraries:

```python
TECHNOLOGY_STACKS = {
    # Animation Libraries
    "animation_libraries": {
        "gsap": {
            "npm": "gsap",
            "use_when": "heavy motion OR complex timelines OR scroll-triggered animations",
            "features": ["timeline", "scrolltrigger", "momentum", "easings"]
        },
        "framer_motion": {
            "npm": "framer-motion",
            "use_when": "React projects with smooth, declarative animations",
            "features": ["variants", "gestures", "layout", "presence"]
        },
        "react_spring": {
            "npm": "@react-spring/web",
            "use_when": "Physics-based spring animations in React",
            "features": ["spring physics", "trail", "decay"]
        },
        "motion_one": {
            "npm": "motion",
            "use_when": "Lightweight, modern alternative to GSAP",
            "features": ["timeline", "scroll", "gestures", "keyframes"]
        },
        "css_animation": {
            "npm": None,
            "use_when": "Simple animations, no dependencies needed",
            "features": ["@keyframes", "transitions", "transforms"]
        }
    },
    
    # 3D Libraries
    "3d_libraries": {
        "threejs": {
            "npm": "three @react-three/fiber @react-three/drei",
            "use_when": "Real 3D with high edge variance (products, objects)",
            "features": ["mesh", "lighting", "materials", "OrbitControls"]
        },
        "babylonjs": {
            "npm": "@babylonjs/core @babylonjs/loaders",
            "use_when": "Enterprise 3D with better tooling, AR/VR support",
            "features": ["scene", "engine", "materials", "physics"]
        },
        "css_3d": {
            "npm": None,
            "use_when": "Simulated 3D with CSS transforms, no WebGL",
            "features": ["perspective", "rotateY", "translateZ", "backface"]
        }
    },
    
    # Text Animation Libraries
    "text_animation": {
        "split_type": {
            "npm": "split-type",
            "use_when": "Character/word/line splitting for animations",
            "features": ["chars", "words", "lines", "gsap integration"]
        },
        "blotter": {
            "npm": "blotter",
            "use_when": "Complex procedural text effects, unusual animations",
            "features": ["unwanted_rotating_roll", "tracking_text_in", "sliding_block"]
        },
        "textillate": {
            "npm": "textillate",
            "use_when": "Simple CSS3 text animations",
            "features": ["in", "out", "sequences", "loop"]
        },
        "css_text": {
            "npm": None,
            "use_when": "Simple text reveals, no dependencies",
            "features": ["clip-path", "mask", "transform"]
        }
    },
    
    # Scroll Libraries
    "scroll_libraries": {
        "lenis": {
            "npm": "lenis",
            "use_when": "Smooth scroll, modern approach, GSAP integration",
            "features": ["smooth scroll", "lerp", "normalize", "stop"]
        },
        "locomotive_scroll": {
            "npm": "locomotive-scroll",
            "use_when": "Parallax effects, scroll-triggered animations",
            "features": ["parallax", "sticky", "sections", "scroll speed"]
        },
        "gsap_scroll": {
            "npm": "gsap (with ScrollTrigger)",
            "use_when": "Scroll-driven animations with GSAP",
            "features": ["scrub", "pin", "snap", "markers"]
        },
        "native_scroll": {
            "npm": None,
            "use_when": "Performance priority, minimal scroll effects",
            "features": ["IntersectionObserver", "CSS scroll-behavior"]
        }
    }
}
```

---

## TECHNOLOGY DETECTION LOGIC

```python
def _detect_technology_stack(self, analysis: Dict, frame: np.ndarray = None) -> Dict:
    """
    Detect which technology stack is needed based on visual analysis.
    """
    brightness_level = analysis.get("brightness_level", "medium")
    motion_level = analysis.get("motion_level", "static")
    depth_perception = analysis.get("depth_perception", "2d")
    edge_score = analysis.get("edge_score", 50)
    scene_changes = analysis.get("scene_changes", 0)
    
    stack = {
        "animation_library": None,
        "3d_library": None,
        "text_animation": None,
        "scroll_effect": None,
        "recommended_packages": [],
        "reasoning": {}
    }
    
    # === ANIMATION LIBRARY DETECTION ===
    
    # Heavy motion → GSAP (most powerful timeline control)
    if motion_level == "heavy":
        stack["animation_library"] = "gsap"
        stack["recommended_packages"].append("gsap")
        stack["reasoning"]["animation"] = "Heavy motion complexity → GSAP"
    
    # Dark + Cinematic → GSAP (Divya's signature style)
    elif brightness_level == "dark" and motion_level != "static":
        stack["animation_library"] = "gsap"
        stack["recommended_packages"].append("gsap")
        stack["reasoning"]["animation"] = "Dark cinematic → GSAP (signature premium style)"
    
    # React + Spring physics needed → react-spring
    elif motion_level == "subtle" and self._detect_physics(frame) if frame else False:
        stack["animation_library"] = "react_spring"
        stack["recommended_packages"].append("@react-spring/web")
        stack["reasoning"]["animation"] = "Subtle + physics → react-spring"
    
    # React + Declarative → Framer Motion
    elif motion_level in ["subtle", "static"]:
        stack["animation_library"] = "framer_motion"
        stack["recommended_packages"].append("framer-motion")
        stack["reasoning"]["animation"] = "React + smooth → Framer Motion"
    
    # Minimal needs → CSS Animation
    else:
        stack["animation_library"] = "css_animation"
        stack["reasoning"]["animation"] = "Minimal motion → CSS Animation"
    
    # === 3D LIBRARY DETECTION ===
    
    if depth_perception == "3d":
        edge_variance = self._detect_edge_variance(frame) if frame else 0.2
        
        if edge_variance > 0.3:
            # Real 3D product/object → Three.js (most popular)
            stack["3d_library"] = "threejs"
            stack["recommended_packages"].extend(["three", "@react-three/fiber", "@react-three/drei"])
            stack["reasoning"]["3d"] = f"Real 3D (edge_variance={edge_variance:.2f}) → Three.js"
        
        elif edge_variance > 0.15:
            # Intermediate → Babylon.js (better for complex scenes)
            stack["3d_library"] = "babylonjs"
            stack["recommended_packages"].extend(["@babylonjs/core", "@babylonjs/loaders"])
            stack["reasoning"]["3d"] = f"Complex 3D (edge_variance={edge_variance:.2f}) → Babylon.js"
        
        else:
            # Simulated 3D → CSS 3D
            stack["3d_library"] = "css_3d"
            stack["reasoning"]["3d"] = "Simulated 3D → CSS 3D transforms"
    
    elif depth_perception == "2.5d":
        stack["3d_library"] = "css_3d"
        stack["reasoning"]["3d"] = "2.5D depth → CSS parallax"
    
    # === TEXT ANIMATION DETECTION ===
    
    # Dark cinematic → SplitType (Divya's signature)
    if brightness_level == "dark":
        stack["text_animation"] = "split_type"
        stack["recommended_packages"].append("split-type")
        stack["reasoning"]["text"] = "Dark cinematic → SplitType"
    
    # Heavy character animation → Blotter (unusual effects)
    elif motion_level == "heavy" and edge_score > 150:
        stack["text_animation"] = "blotter"
        stack["recommended_packages"].append("blotter")
        stack["reasoning"]["text"] = "Heavy + complex text → Blotter"
    
    # Simple CSS text animation
    elif motion_level == "subtle":
        stack["text_animation"] = "textillate"
        stack["recommended_packages"].append("textillate")
        stack["reasoning"]["text"] = "Simple text → Textillate"
    
    else:
        stack["text_animation"] = "css_text"
        stack["reasoning"]["text"] = "Minimal text → CSS"
    
    # === SCROLL LIBRARY DETECTION ===
    
    # Multiple scene changes → Smooth scroll needed
    if scene_changes > 3:
        # Parallax heavy → Locomotive Scroll
        if edge_score > 100:
            stack["scroll_effect"] = "locomotive_scroll"
            stack["recommended_packages"].append("locomotive-scroll")
            stack["reasoning"]["scroll"] = f"{scene_changes} scenes + parallax → Locomotive Scroll"
        
        # GSAP ScrollTrigger
        elif motion_level == "heavy":
            stack["scroll_effect"] = "gsap_scroll"
            stack["reasoning"]["scroll"] = "Heavy scroll animation → GSAP ScrollTrigger"
        
        # Modern smooth → Lenis
        else:
            stack["scroll_effect"] = "lenis"
            stack["recommended_packages"].append("lenis")
            stack["reasoning"]["scroll"] = "Smooth modern scroll → Lenis"
    
    return stack

def _detect_edge_variance(self, frame: np.ndarray) -> float:
    """Detect real 3D vs simulated."""
    if frame is None:
        return 0.2
    gray = np.mean(frame, axis=2)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    return float(np.var(sobel_magnitude) / (np.mean(sobel_magnitude) + 1e-10))

def _detect_physics(self, frame: np.ndarray) -> bool:
    """Detect if physics-based animation is needed."""
    # High motion with damping suggests spring physics
    if frame is not None:
        brightness_std = np.std(frame)
        return brightness_std > 30
    return False
```

---

## GENERATION METHODS FOR ALL LIBRARIES

### generate_animation_code(params: Dict, stack: Dict) -> Dict

```python
def generate_animation_code(self, params: Dict, stack: Dict) -> Dict:
    """Generate animation code for detected stack."""
    result = {
        "animation_code": None,
        "3d_code": None,
        "text_code": None,
        "scroll_code": None,
        "imports": [],
        "packages": [],
        "technology_used": []
    }
    
    # === ANIMATION ===
    anim_lib = stack.get("animation_library")
    
    if anim_lib == "gsap":
        result["animation_code"] = self._generate_gsap(params)
        result["imports"].extend([
            "import { gsap } from 'gsap'",
            "import { ScrollTrigger } from 'gsap/ScrollTrigger'",
            "import { Draggable } from 'gsap/Draggable' if needed"
        ])
        result["packages"].append("gsap")
        result["technology_used"].append("GSAP")
    
    elif anim_lib == "framer_motion":
        result["animation_code"] = self._generate_framer_motion(params)
        result["imports"].append("import { motion } from 'framer-motion'")
        result["packages"].append("framer-motion")
        result["technology_used"].append("Framer Motion")
    
    elif anim_lib == "react_spring":
        result["animation_code"] = self._generate_react_spring(params)
        result["imports"].append("import { useSpring, animated } from '@react-spring/web'")
        result["packages"].append("@react-spring/web")
        result["technology_used"].append("React Spring")
    
    elif anim_lib == "motion_one":
        result["animation_code"] = self._generate_motion_one(params)
        result["imports"].extend([
            "import { animate, timeline, scroll } from 'motion'",
            "import 'motion/dist/style.css'"
        ])
        result["packages"].append("motion")
        result["technology_used"].append("Motion One")
    
    elif anim_lib == "css_animation":
        result["animation_code"] = self._generate_css_animation(params)
        result["technology_used"].append("CSS Animation")
    
    # === 3D ===
    d3_lib = stack.get("3d_library")
    
    if d3_lib == "threejs":
        result["3d_code"] = self._generate_threejs(params)
        result["imports"].extend([
            "import * as THREE from 'three'",
            "import { Canvas } from '@react-three/fiber'",
            "import { OrbitControls, Environment, Float } from '@react-three/drei'"
        ])
        result["packages"].extend(["three", "@react-three/fiber", "@react-three/drei"])
        result["technology_used"].append("Three.js/R3F")
    
    elif d3_lib == "babylonjs":
        result["3d_code"] = self._generate_babylonjs(params)
        result["imports"].extend([
            "import * as BABYLON from '@babylonjs/core'",
            "import '@babylonjs/loaders'"
        ])
        result["packages"].extend(["@babylonjs/core", "@babylonjs/loaders"])
        result["technology_used"].append("Babylon.js")
    
    elif d3_lib == "css_3d":
        result["3d_code"] = self._generate_css_3d(params)
        result["technology_used"].append("CSS 3D")
    
    # === TEXT ===
    text_lib = stack.get("text_animation")
    
    if text_lib == "split_type":
        result["text_code"] = self._generate_split_type(params)
        result["imports"].append("import SplitType from 'split-type'")
        result["packages"].append("split-type")
        result["technology_used"].append("SplitType")
    
    elif text_lib == "blotter":
        result["text_code"] = self._generate_blotter(params)
        result["imports"].append("import Blotter from 'blotter'")
        result["packages"].append("blotter")
        result["technology_used"].append("Blotter")
    
    elif text_lib == "textillate":
        result["text_code"] = self._generate_textillate(params)
        result["imports"].append("import 'textillate/assets/textillate.css'")
        result["packages"].append("textillate")
        result["technology_used"].append("Textillate")
    
    elif text_lib == "css_text":
        result["text_code"] = self._generate_css_text(params)
        result["technology_used"].append("CSS Text")
    
    # === SCROLL ===
    scroll_lib = stack.get("scroll_effect")
    
    if scroll_lib == "lenis":
        result["scroll_code"] = self._generate_lenis(params)
        result["imports"].append("import Lenis from 'lenis'")
        result["packages"].append("lenis")
        result["technology_used"].append("Lenis")
    
    elif scroll_lib == "locomotive_scroll":
        result["scroll_code"] = self._generate_locomotive(params)
        result["imports"].append("import LocomotiveScroll from 'locomotive-scroll'")
        result["packages"].append("locomotive-scroll")
        result["technology_used"].append("Locomotive Scroll")
    
    elif scroll_lib == "gsap_scroll":
        result["scroll_code"] = self._generate_gsap_scroll(params)
        result["technology_used"].append("GSAP ScrollTrigger")
    
    elif scroll_lib == "native_scroll":
        result["scroll_code"] = self._generate_native_scroll(params)
        result["technology_used"].append("Native Scroll")
    
    return result
```

---

## _generate_gsap(params: Dict) -> str

```python
def _generate_gsap(self, params: Dict) -> str:
    """GSAP animation - chosen for heavy motion, complex timelines, Divya's signature."""
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
// GSAP Animation - Auto-generated (motion_level: {motion_level})
import {{ useEffect }} from 'react'
import {{ gsap }} from 'gsap'
import {{ ScrollTrigger }} from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useGSAPAnimation() {{
  useEffect(() => {{
    // Master timeline
    const tl = gsap.timeline()

    // Navbar entrance
    tl.from('.navbar', {{
      y: -100,
      opacity: 0,
      duration: 0.8,
      ease: '{ease}'
    }})

    // Hero title - character stagger (if using SplitType)
    tl.from('.hero-title .char', {{
      y: 100,
      opacity: 0,
      stagger: {stagger},
      duration: {duration},
      ease: '{ease}'
    }}, 0.2)

    // Subtitle
    tl.from('.hero-subtitle', {{
      y: 50,
      opacity: 0,
      duration: {duration * 0.8},
      ease: '{ease}'
    }}, 0.4)

    // CTA
    tl.from('.hero-cta', {{
      scale: 0.8,
      opacity: 0,
      duration: 0.5,
      ease: 'back.out(1.7)'
    }}, 0.6)

    // Scroll indicator bounce
    gsap.to('.scroll-indicator', {{
      y: 10,
      duration: 1,
      repeat: -1,
      yoyo: true,
      ease: 'power1.inOut'
    }})

    // Scroll-triggered sections
    gsap.utils.toArray('.scroll-reveal').forEach((el) => {{
      gsap.from(el, {{
        y: 100,
        opacity: 0,
        duration: 1,
        scrollTrigger: {{
          trigger: el,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        }}
      }})
    }})

    // Parallax on scroll
    gsap.utils.toArray('.parallax').forEach((el) => {{
      gsap.to(el, {{
        y: -50,
        scrollTrigger: {{
          trigger: el,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1
        }}
      }})
    }})

    return () => {{
      tl.kill()
      ScrollTrigger.getAll().forEach(st => st.kill())
    }}
  }}, [])
}}
"""
```

---

## _generate_react_spring(params: Dict) -> str

```python
def _generate_react_spring(self, params: Dict) -> str:
    """React Spring - chosen for physics-based subtle animations."""
    return """
// React Spring Animation - Auto-generated
import { useSpring, animated } from '@react-spring/web'

export function useHeroSpring() {
  // Navbar spring
  const navbarSpring = useSpring({
    from: { y: -100, opacity: 0 },
    to: { y: 0, opacity: 1 },
    config: { tension: 200, friction: 20 }
  })

  // Title fade up
  const titleSpring = useSpring({
    from: { y: 50, opacity: 0 },
    to: { y: 0, opacity: 1 },
    delay: 200,
    config: { tension: 180, friction: 12 }
  })

  // Subtitle
  const subtitleSpring = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    delay: 400,
    config: { tension: 150, friction: 15 }
  })

  // CTA button scale
  const ctaSpring = useSpring({
    from: { scale: 0.8, opacity: 0 },
    to: { scale: 1, opacity: 1 },
    delay: 600,
    config: { tension: 200, friction: 10 }
  })

  return {{ navbarSpring, titleSpring, subtitleSpring, ctaSpring }}
}

// Component usage:
// <animated.div style={{ y: navbarSpring.y }} className="navbar">...</animated.div>
"""
```

---

## _generate_motion_one(params: Dict) -> str

```python
def _generate_motion_one(self, params: Dict) -> str:
    """Motion One - lightweight modern animation library."""
    return """
// Motion One Animation - Auto-generated
import { animate, timeline, scroll } from 'motion'

// Entrance sequence
const sequence = timeline([
  ['.navbar', { y: [-100, 0], opacity: [0, 1] }, { duration: 0.6 }],
  ['.hero-title', { y: [50, 0], opacity: [0, 1] }, { duration: 0.6, at: 0.2 }],
  ['.hero-subtitle', { y: [30, 0], opacity: [0, 1] }, { duration: 0.5, at: 0.4 }],
  ['.hero-cta', { scale: [0.8, 1], opacity: [0, 1] }, { duration: 0.4, at: 0.6 }]
], {
  easing: 'ease-out'
})

// Run on mount
document.addEventListener('DOMContentLoaded', () => {
  sequence.play()
})

// Scroll-triggered reveal
const scrollReveal = document.querySelectorAll('.scroll-reveal')
scrollReveal.forEach((el) => {
  scroll(({ x }) => [el, { y: [50, 0], opacity: [0, 1] }], {
    target: el,
    offset: ['start end', 'end start']
  })
})
"""
```

---

## _generate_babylonjs(params: Dict) -> str

```python
def _generate_babylonjs(self, params: Dict) -> str:
    """Babylon.js - chosen for complex 3D scenes, enterprise projects."""
    lighting_type = params.get("lighting_type", "ambient")
    
    if lighting_type == "spotlight":
        lights = """
        var light = new BABYLON.SpotLight(
            "spotLight",
            new BABYLON.Vector3(0, 10, 0),
            new BABYLON.Vector3(0, -1, 0),
            Math.PI / 3,
            2,
            scene
        );
        """
    else:
        lights = """
        var light = new BABYLON.HemisphericLight(
            "light",
            new BABYLON.Vector3(0, 1, 0),
            scene
        );
        light.intensity = 0.8;
        """
    
    return f"""
// Babylon.js 3D Scene - Auto-generated
import * as BABYLON from '@babylonjs/core'
import '@babylonjs/loaders'

export function createBabylonScene(canvas: HTMLCanvasElement) {{
  const engine = new BABYLON.Engine(canvas, true, {{
    preserveDrawingBuffer: true,
    stencil: true
  }})

  const scene = new BABYLON.Scene(engine)
  scene.clearColor = new BABYLON.Color4(0, 0, 0, 1)

  // Camera
  const camera = new BABYLON.ArcRotateCamera(
    "camera",
    Math.PI / 2,
    Math.PI / 2,
    5,
    BABYLON.Vector3.Zero(),
    scene
  )
  camera.attachControl(canvas, true)
  camera.wheelPrecision = 50

  // Lighting
  {lights}

  // Main mesh - sphere with PBR material
  const sphere = BABYLON.MeshBuilder.CreateSphere("sphere", {{ diameter: 2 }}, scene)
  const pbr = new BABYLON.PBRMaterial("pbr", scene)
  pbr.metallic = 0.8
  pbr.roughness = 0.2
  pbr.albedoColor = BABYLON.Color3.FromHexString("#8a2be2")
  sphere.material = pbr

  // Environment
  const envHelper = BABYLON.EnvironmentHelper.CreateAsync(scene)

  // Animation loop
  scene.registerBeforeRender(() => {{
    sphere.rotation.y += 0.01
    sphere.rotation.x += 0.005
  }})

  // Render loop
  engine.runRenderLoop(() => {{
    scene.render()
  }})

  // Resize handler
  window.addEventListener('resize', () => {{
    engine.resize()
  }})

  return {{ scene, engine }}
}}
"""
```

---

## _generate_blotter(params: Dict) -> str

```python
def _generate_blotter(self, params: Dict) -> str:
    """Blotter.js - complex procedural text effects."""
    motion_level = params.get("motion_level", "subtle")
    
    if motion_level == "heavy":
        effect = "UnwantedRotatingRoll"
        effect_opts = "{ speed: 0.6 }"
    else:
        effect = "TrackingTextIn"
        effect_opts = "{ trackSpeed: 1.5, trackStagger: 0.05 }"
    
    return f"""
// Blotter.js Text Animation - Auto-generated
import {{ useEffect, useRef }} from 'react'
import Blotter from 'blotter'
import {{ {effect} }} from 'blotter'
import gsap from 'gsap'

export function BlotterText({{ text, className }}) {{
  const containerRef = useRef(null)
  const blotterRef = useRef(null)

  useEffect(() => {{
    if (!containerRef.current) return

    // Create Blotter text
    const text = new Blotter.Text('{text}', {{
      family: 'Georgia, serif',
      size: 72,
      fill: '#ffffff'
    }})

    // Apply effect
    const {effect} = Blotter.{effect}
    const blotter = new Blotter({effect}, {{
      texts: [text]
    }})

    blotterRef.current = blotter

    // Target the element
    blotter.buildFor(containerRef.current)

    // GSAP entrance animation
    gsap.from(containerRef.current, {{
      opacity: 0,
      y: 50,
      duration: 1,
      ease: 'power3.out'
    }})

    return () => {{
      if (blotterRef.current) {{
        blotterRef.current = null
      }}
    }}
  }}, [text])

  return (
    <div ref={{containerRef}} className={{className}} />
  )
}}
"""
```

---

## _generate_textillate(params: Dict) -> str

```python
def _generate_textillate(self, params: Dict) -> str:
    """Textillate - simple CSS3 text animations."""
    return """
// Textillate Animation - Auto-generated
import { useEffect, useRef } from 'react'
import 'textillate/assets/textillate.css'
import $ from 'jquery'
import 'textillate'

export function TextillateText({{ text, className, options }}) {{
  const ref = useRef(null)

  useEffect(() => {{
    if (!ref.current) return

    const $el = $(ref.current)
    
    $el.textillate({
      initialDelay: 100,
      in: {{
        effect: 'fadeInUpBig',
        delayScale: 1.5,
        delay: 50,
        sync: false
      }},
      out: {{
        effect: 'fadeOutDownBig',
        sync: true
      }},
      loop: false,
      ...options
    })

    return () => {{
      $el.textillate('stop')
    }}
  }}, [text, options])

  return (
    <div ref={{ref}} className={`tlt ${className || ''}`}}>
      <ul className="texts">
        <li>{{text}}</li>
      </ul>
    </div>
  )
}}
"""
```

---

## _generate_locomotive(params: Dict) -> str

```python
def _generate_locomotive(self, params: Dict) -> str:
    """Locomotive Scroll - parallax effects, smooth scroll."""
    return """
// Locomotive Scroll - Auto-generated
import { useEffect } from 'react'
import LocomotiveScroll from 'locomotive-scroll'
import 'locomotive-scroll/dist/locomotive-scroll.css'

export function useLocomotiveScroll() {{
  useEffect(() => {{
    const scroll = new LocomotiveScroll({
      el: document.querySelector('[data-scroll-container]'),
      smooth: true,
      lerp: 0.1,
      multiplier: 0.8,
      getDirection: true,
      useKeyboard: true
    })

    // Update on resize
    scroll.on('scroll', (args) => {{
      document.documentElement.setAttribute(
        'data-direction',
        args.direction
      )
    }})

    // Smooth scroll to element
    const scrollTo = (target) => {{
      scroll.scrollTo(target)
    }}

    return () => {{
      if (scroll) scroll.destroy()
    }}
  }}, [])
}}

// Parallax data attribute usage:
// <div data-scroll data-scroll-speed="1">Content</div>
// <div data-scroll data-scroll-repeat>Repeating on scroll</div>
"""
```

---

## _generate_gsap_scroll(params: Dict) -> str

```python
def _generate_gsap_scroll(self, params: Dict) -> str:
    """GSAP ScrollTrigger - scroll-driven animations."""
    return """
// GSAP ScrollTrigger - Auto-generated
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useScrollAnimations() {{
  // Horizontal scroll section
  const horizontalSections = document.querySelectorAll('.horizontal-scroll')
  horizontalSections.forEach((section) => {{
    const panels = section.querySelectorAll('.panel')
    gsap.to(panels, {
      xPercent: -100 * (panels.length - 1),
      x: () => section.scrollWidth - section.clientWidth,
      scrollTrigger: {
        trigger: section,
        start: 'top top',
        end: () => '+=' + section.scrollWidth,
        scrub: 1,
        pin: true,
        anticipatePin: 1
      }
    })
  }})

  // Fade up on scroll
  gsap.utils.toArray('.fade-up').forEach((el) => {{
    gsap.from(el, {
      y: 100,
      opacity: 0,
      duration: 1,
      scrollTrigger: {
        trigger: el,
        start: 'top 80%',
        toggleActions: 'play none none reverse'
      }
    })
  }})

  // Scale reveal
  gsap.utils.toArray('.scale-reveal').forEach((el) => {{
    gsap.from(el, {
      scale: 0.8,
      opacity: 0,
      duration: 0.8,
      scrollTrigger: {
        trigger: el,
        start: 'top 80%'
      }
    })
  }})

  // Snap to sections
  ScrollTrigger.create({
    snap: {
      snapTo: 'labels',
      duration: { min: 0.2, max: 0.5 },
      ease: 'power1.inOut',
      delay: 0.1
    }
  })
}}
"""
```

---

## _generate_native_scroll(params: Dict) -> str

```python
def _generate_native_scroll(self, params: Dict) -> str:
    """Native scroll with IntersectionObserver."""
    return """
// Native Scroll with IntersectionObserver - Auto-generated
import { useEffect, useRef } from 'react'

export function useNativeScrollReveal() {{
  useEffect(() => {{
    const observerOptions = {{
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    }}

    const observer = new IntersectionObserver((entries) => {{
      entries.forEach((entry) => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('revealed')
          // Optional: unobserve after reveal
          // observer.unobserve(entry.target)
        }}
      }})
    }}, observerOptions)

    // Observe all elements with scroll-reveal class
    document.querySelectorAll('.scroll-reveal').forEach((el) => {{
      observer.observe(el)
    }})

    return () => observer.disconnect()
  }}, [])
}}

// CSS for reveal:
// .scroll-reveal {
//   opacity: 0;
//   transform: translateY(50px);
//   transition: opacity 0.6s ease, transform 0.6s ease;
// }
// .scroll-reveal.revealed {
//   opacity: 1;
//   transform: translateY(0);
// }
"""
```

---

## TECHNOLOGY DETECTION DECISION TREE

```
Input Analysis
    │
    ├─ motion_level = heavy?
    │   └─ YES → GSAP (animation)
    │   └─ NO → brightness = dark?
    │       └─ YES → GSAP (animation)
    │       └─ NO → React + physics?
    │           └─ YES → React Spring
    │           └─ NO → React?
    │               └─ YES → Framer Motion
    │               └─ NO → CSS Animation
    │
    ├─ depth_perception = 3D?
    │   └─ YES → edge_variance > 0.3?
    │       └─ YES → Three.js
    │       └─ NO → edge_variance > 0.15?
    │           └─ YES → Babylon.js
    │           └─ NO → CSS 3D
    │   └─ NO → 2.5D?
    │       └─ YES → CSS 3D
    │       └─ NO → (no 3D)
    │
    ├─ brightness = dark?
    │   └─ YES → SplitType (text)
    │   └─ NO → motion = heavy + high edge?
    │       └─ YES → Blotter (text)
    │       └─ NO → (simple text)
    │           └─ Textillate or CSS Text
    │
    └─ scene_changes > 3?
        └─ YES → edge_score > 100?
            └─ YES → Locomotive Scroll
            └─ NO → motion = heavy?
                └─ YES → GSAP ScrollTrigger
                └─ NO → Lenis
        └─ NO → Native Scroll
```

---

## PACKAGE INSTALLATION GUIDE

```bash
# Animation Libraries (install based on detection)
npm install gsap
npm install framer-motion
npm install @react-spring/web
npm install motion

# 3D Libraries (install based on detection)
npm install three @react-three/fiber @react-three/drei
npm install @babylonjs/core @babylonjs/loaders

# Text Animation (install based on detection)
npm install split-type
npm install blotter
npm install textillate

# Scroll Libraries (install based on detection)
npm install lenis
npm install locomotive-scroll

# Peer dependencies (install these too)
npm install jquery  # For Textillate
npm install react react-dom  # For React libraries
```

---

## EXAMPLE OUTPUT

```python
result = design.build_from_input("https://instagram.com/reel/xyz")

# technology_stack:
{
    "animation_library": "gsap",
    "3d_library": "threejs",
    "text_animation": "split_type",
    "scroll_effect": "locomotive_scroll",
    "recommended_packages": [
        "gsap", "three", "@react-three/fiber", "@react-three/drei",
        "split-type", "locomotive-scroll"
    ],
    "reasoning": {
        "animation": "Heavy motion complexity → GSAP",
        "3d": "Real 3D (edge_variance=0.42) → Three.js",
        "text": "Dark cinematic → SplitType",
        "scroll": "5 scenes + parallax → Locomotive Scroll"
    }
}

# result.packages:
["gsap", "three", "@react-three/fiber", "@react-three/drei", "split-type", "locomotive-scroll"]

# result.technology_used:
["GSAP", "Three.js/R3F", "SplitType", "Locomotive Scroll"]
```

---

## DIVYA'S SIGNATURE TECHNIQUES

When dark cinematic + heavy motion is detected, use Divya's exact patterns:

| Pattern | Technology | Implementation |
|---------|------------|---------------|
| Mouse spotlight | GSAP | Track mouse position, update CSS variables |
| Character stagger | SplitType + GSAP | Split text, animate chars with stagger |
| 3D product rotate | Three.js | Sphere with PBR material, rotation animation |
| Smooth scroll | Lenis | Lerp: 0.1, smooth: true |
| Gradient overlay | CSS | Linear gradient dark at bottom |
| Vignette | CSS | Box-shadow inset |

---

END OF SYSTEM v3.2
