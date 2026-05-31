# ULTRA-PRECISE PROMPT: Cinematic Design Code Generation
## Read EVERY line carefully. Missing ANY method = FAILURE.

---

## EXISTING FILE: `neuro/skills/cinematic_design.py`

The file EXISTS and has these working methods:
- `download_and_extract(url)` ✅
- `analyze_single_image(source)` ✅
- `analyze_video_frames(frames)` ✅
- `analyze_description(text)` ✅
- `detect_technology_stack(analysis)` ✅
- `invoke(task, context)` ✅
- Helper methods (HSV, edge detection, color extraction, etc.) ✅

---

## ADD THIS ONE METHOD: `generate_code(analysis, content)`

Add this method to the `CinematicDesign` class. This is the ONLY method you need to add.

```python
def generate_code(self, analysis: dict[str, Any], content: dict[str, str] | None = None) -> dict[str, Any]:
    """
    Generate complete code based on detected technology stack.
    
    This is the MAIN output method. It must generate REAL, WORKING code.
    
    Args:
        analysis: Dict from analyze_video_frames() or analyze_description()
        content: Optional dict with "title", "subtitle", "cta"
    
    Returns:
        {
            "css": str,           # Valid CSS code
            "jsx": str,           # Valid React/JSX code  
            "npm_packages": list,  # NPM packages to install
            "components": list,    # Component names created
            "technology_stack": dict  # What was used and why
        }
    """
    content = content or {"title": "Premium", "subtitle": "Cinematic", "cta": "Explore"}
    
    # Get detected stack
    tech_stack = self.detect_technology_stack(analysis)
    
    # Get animation library
    anim = tech_stack["animation_library"]  # "gsap" or "framer_motion" or "css_animation" etc.
    d3 = tech_stack["3d_library"]  # "threejs" or "babylonjs" or "css_3d" or None
    text_anim = tech_stack["text_animation"]  # "split_type" or "blotter" or "css_text" or None
    scroll = tech_stack["scroll_effect"]  # "lenis" or "locomotive_scroll" or "gsap_scroll" or "native_scroll" or None
    
    packages = []
    css_parts = []
    jsx_parts = []
    components = []
    stack_info = {"animation": anim, "3d": d3, "text": text_anim, "scroll": scroll}
    
    # 1. ANIMATION CODE
    if anim == "gsap":
        css_parts.append(self._generate_gsap_css(analysis))
        jsx_parts.append(self._generate_gsap_jsx())
        packages.extend(["gsap"])
        components.append("GSAPAnimation")
    elif anim == "framer_motion":
        css_parts.append(self._generate_framer_css(analysis))
        jsx_parts.append(self._generate_framer_jsx())
        packages.extend(["framer-motion"])
        components.append("FramerHero")
    else:  # css_animation
        css_parts.append(self._generate_css_animation(analysis))
        jsx_parts.append(self._generate_basic_jsx(content))
        components.append("CSSHero")
    
    # 2. 3D CODE (if needed)
    if d3 == "threejs":
        css_parts.append(self._generate_threejs_css())
        jsx_parts.append(self._generate_threejs_jsx(analysis))
        packages.extend(["three", "@react-three/fiber", "@react-three/drei"])
        components.append("ThreeScene")
    elif d3 == "babylonjs":
        css_parts.append(self._generate_babylonjs_css())
        jsx_parts.append(self._generate_babylonjs_jsx(analysis))
        packages.extend(["@babylonjs/core", "@babylonjs/loaders"])
        components.append("BabylonScene")
    elif d3 == "css_3d":
        css_parts.append(self._generate_css_3d(analysis))
        # CSS 3D uses same JSX, no extra component
    
    # 3. TEXT ANIMATION (if needed)
    if text_anim == "split_type":
        jsx_parts.append(self._generate_splittext_jsx())
        packages.append("split-type")
        components.append("SplitText")
    elif text_anim == "blotter":
        jsx_parts.append(self._generate_blotter_jsx())
        packages.append("blotter")
        components.append("BlotterText")
    
    # 4. SCROLL (if needed)
    if scroll == "lenis":
        css_parts.append(self._generate_lenis_css())
        jsx_parts.append(self._generate_lenis_jsx())
        packages.append("lenis")
        components.append("LenisScroll")
    elif scroll == "locomotive_scroll":
        css_parts.append(self._generate_locomotive_css())
        jsx_parts.append(self._generate_locomotive_jsx())
        packages.append("locomotive-scroll")
        components.append("LocomotiveScroll")
    elif scroll == "gsap_scroll":
        # GSAP scroll uses existing GSAP code
        pass
    
    return {
        "css": "\n\n".join(css_parts),
        "jsx": "\n\n".join(jsx_parts),
        "npm_packages": list(set(packages)),
        "components": components,
        "technology_stack": stack_info
    }
```

---

## REQUIRED SUB-METHODS

Add ALL of these methods to the class. Each must return VALID code.

### 1. `_generate_gsap_css(analysis) -> str`

```python
def _generate_gsap_css(self, analysis: dict[str, Any]) -> str:
    """Generate GSAP CSS keyframes and classes."""
    motion = analysis.get("motion_level", "subtle")
    if motion == "heavy":
        duration = "0.4"
        stagger = "0.05"
    else:
        duration = "0.6"
        stagger = "0.15"
    
    return f"""
/* GSAP Animations */
@keyframes fade-up {{
  from {{ opacity: 0; transform: translateY(50px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes scale-in {{
  from {{ opacity: 0; transform: scale(0.9); }}
  to {{ opacity: 1; transform: scale(1); }}
}}

.gsap-hero {{ position: relative; overflow: hidden; }}
.gsap-title {{ animation: fade-up {duration}s ease-out forwards; }}
.gsap-subtitle {{ animation: fade-up {duration}s ease-out {float(stagger) * 1}s forwards; opacity: 0; }}
.gsap-cta {{ animation: scale-in {duration}s ease-out {float(stagger) * 2}s forwards; opacity: 0; }}
.scroll-indicator {{ animation: bounce 2s infinite; }}
@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(10px); }}
}}
"""
```

### 2. `_generate_gsap_jsx() -> str`

```python
def _generate_gsap_jsx(self) -> str:
    return """
import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function GSAPAnimation({ title, subtitle, cta }) {
  const containerRef = useRef(null)
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.gsap-title', { y: 100, opacity: 0, duration: 0.8, ease: 'expo.out' })
      gsap.from('.gsap-subtitle', { y: 50, opacity: 0, duration: 0.6, delay: 0.2, ease: 'expo.out' })
      gsap.from('.gsap-cta', { scale: 0.8, opacity: 0, duration: 0.5, delay: 0.4, ease: 'back.out(1.7)' })
    }, containerRef)
    
    return () => ctx.revert()
  }, [])
  
  return (
    <div ref={containerRef} className="gsap-hero">
      <h1 className="gsap-title">{title || 'Premium'}</h1>
      <p className="gsap-subtitle">{subtitle || 'Cinematic'}</p>
      <button className="gsap-cta">{cta || 'Explore'}</button>
    </div>
  )
}
"""
```

### 3. `_generate_framer_css(analysis) -> str`

```python
def _generate_framer_css(self, analysis: dict[str, Any]) -> str:
    return """
/* Framer Motion Animations */
.framer-hero { position: relative; overflow: hidden; }
"""
```

### 4. `_generate_framer_jsx() -> str`

```python
def _generate_framer_jsx(self) -> str:
    return """
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.2 } }
}

const item = {
  hidden: { opacity: 0, y: 50 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 80, damping: 15 } }
}

export function FramerHero({ title, subtitle, cta }) {
  return (
    <motion.div className="framer-hero" variants={container} initial="hidden" animate="visible">
      <motion.h1 className="framer-title" variants={item}>{title || 'Premium'}</motion.h1>
      <motion.p className="framer-subtitle" variants={item}>{subtitle || 'Cinematic'}</motion.p>
      <motion.button className="framer-cta" variants={item} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        {cta || 'Explore'}
      </motion.button>
    </motion.div>
  )
}
"""
```

### 5. `_generate_css_animation(analysis) -> str`

```python
def _generate_css_animation(self, analysis: dict[str, Any]) -> str:
    motion = analysis.get("motion_level", "subtle")
    duration = "0.5s" if motion == "subtle" else "0.3s"
    
    return f"""
/* CSS Animation Hero */
@keyframes fade-up {{
  from {{ opacity: 0; transform: translateY(40px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.css-hero {{ position: relative; }}
.css-hero h1 {{ animation: fade-up {duration} ease-out forwards; }}
.css-hero p {{ animation: fade-up {duration} ease-out 0.2s forwards; opacity: 0; }}
.css-hero button {{ animation: fade-up {duration} ease-out 0.4s forwards; opacity: 0; }}
"""
```

### 6. `_generate_threejs_css() -> str`

```python
def _generate_threejs_css(self) -> str:
    return """
/* Three.js Scene */
.three-canvas { width: 100%; height: 100vh; position: absolute; top: 0; left: 0; z-index: 0; }
.three-content { position: relative; z-index: 1; }
"""
```

### 7. `_generate_threejs_jsx(analysis) -> str`

```python
def _generate_threejs_jsx(self, analysis: dict[str, Any]) -> str:
    lighting = analysis.get("lighting_type", "ambient")
    
    lights = """
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
    """
    if lighting == "spotlight":
        lights = """
      <spotLight position={[0, 10, 0]} angle={0.3} penumbra={1} intensity={1.5} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
    """
    
    return f"""
import {{ Canvas }} from '@react-three/fiber'
import {{ OrbitControls, Environment }} from '@react-three/drei'

export function ThreeScene() {{
  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        {lights}
        <mesh>
          <sphereGeometry args={{[1, 32, 32]}} />
          <meshStandardMaterial color="#8a2be2" metalness={0.8} roughness={0.2}} />
        </mesh>
        <OrbitControls enableZoom={{false}} autoRotate autoRotateSpeed={{0.5}} />
      </Canvas>
    </div>
  )
}}
"""
```

### 8. `_generate_babylonjs_css() -> str`

```python
def _generate_babylonjs_css(self) -> str:
    return """
/* Babylon.js Scene */
.babylon-canvas { width: 100%; height: 100vh; }
.babylon-content { position: relative; z-index: 1; }
"""
```

### 9. `_generate_babylonjs_jsx(analysis) -> str`

```python
def _generate_babylonjs_jsx(self, analysis: dict[str, Any]) -> str:
    return """
export function BabylonScene({ canvasId }) {
  // Initialize in useEffect with:
  // const { Engine, Scene, ArcRotateCamera, HemisphericLight, Vector3, MeshBuilder } = await import('@babylonjs/core')
  return (
    <canvas id={canvasId || 'babylon-canvas'} className="babylon-canvas" />
  )
}
"""
```

### 10. `_generate_css_3d(analysis) -> str`

```python
def _generate_css_3d(self, analysis: dict[str, Any]) -> str:
    edge = analysis.get("edge_score", 100)
    depth = min(edge / 50, 5)
    
    return f"""
/* CSS 3D Transforms */
.scene-3d {{ transform-style: preserve-3d; perspective: 1000px; }}
.layer-1 {{ transform: translateZ({depth}px); }}
.layer-2 {{ transform: translateZ({depth * 0.7}px); }}
.layer-3 {{ transform: translateZ({depth * 0.4}px); }}
.card-3d {{ transform-style: preserve-3d; transition: transform 0.8s; }}
.card-3d:hover {{ transform: rotateY(180deg); }}
"""
```

### 11. `_generate_splittext_jsx() -> str`

```python
def _generate_splittext_jsx(self) -> str:
    return """
import { useEffect, useRef } from 'react'
import SplitType from 'split-type'

export function SplitText({ text, className }) {
  const ref = useRef(null)
  
  useEffect(() => {
    if (!ref.current) return
    const split = new SplitType(ref.current, { types: 'chars' })
    
    return () => split.revert()
  }, [text])
  
  return <div ref={ref} className={className}>{text}</div>
}
"""
```

### 12. `_generate_blotter_jsx() -> str`

```python
def _generate_blotter_jsx(self) -> str:
    return """
import { useEffect, useRef } from 'react'
import Blotter from 'blotter'
import { RollingDistortMaterial } from 'blotter'

export function BlotterText({ text, className }) {
  const ref = useRef(null)
  
  useEffect(() => {
    if (!ref.current) return
    const material = new Blotter.RollingDistortMaterial()
    const blotter = new Blotter([material], { texts: [text] })
    blotter.buildFor(ref.current)
    return () => blotter.running = false
  }, [text])
  
  return <div ref={ref} className={className} />
}
"""
```

### 13. `_generate_lenis_css() -> str`

```python
def _generate_lenis_css(self) -> str:
    return """
/* Lenis Smooth Scroll */
html.lenis { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto; }
[data-lenis-scroll] { y: calc(var(--scroll) * 1px); }
"""
```

### 14. `_generate_lenis_jsx() -> str`

```python
def _generate_lenis_jsx(self) -> str:
    return """
import { useEffect } from 'react'
import Lenis from 'lenis'

export function LenisProvider({ children }) {
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) })
    
    function raf(time) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }
    requestAnimationFrame(raf)
    
    return () => lenis.destroy()
  }, [])
  
  return <>{children}</>
}
"""
```

### 15. `_generate_locomotive_css() -> str`

```python
def _generate_locomotive_css(self) -> str:
    return """
/* Locomotive Scroll */
[data-scroll-container] { perspective: 1px; overflow: hidden; }
[data-scroll] { will-change: transform; }
[data-scroll-speed="1"] { transform: translateY(calc(var(--scroll) * 1px)); }
[data-scroll-speed="-1"] { transform: translateY(calc(var(--scroll) * -1px)); }
"""
```

### 16. `_generate_locomotive_jsx() -> str`

```python
def _generate_locomotive_jsx(self) -> str:
    return """
import { useEffect } from 'react'
import LocomotiveScroll from 'locomotive-scroll'

export function LocomotiveProvider({ children }) {
  useEffect(() => {
    const scroll = new LocomotiveScroll()
    return () => scroll.destroy()
  }, [])
  
  return <div data-scroll-container>{children}</div>
}
"""
```

---

## ALSO ADD THIS METHOD: `build_from_input()`

Add this method - it's currently MISSING but called by `invoke()`:

```python
def build_from_input(self, input_data: str, content: dict[str, str] | None = None) -> dict[str, Any]:
    """
    Main entry point. Analyzes input and generates code.
    
    Args:
        input_data: URL, file path, or text description
        content: Optional dict with "title", "subtitle", "cta"
    
    Returns:
        Dict with analysis_metadata, css, jsx, npm_packages, components
    """
    # Analyze the input
    if self._looks_like_url(input_data):
        if self._looks_like_video(input_data) or any(ext in input_data.lower() for ext in ['youtube', 'instagram', 'tiktok', 'twitter']):
            frames = self.download_and_extract(input_data)
            analysis = self.analyze_video_frames(frames)
        elif self._looks_like_image(input_data):
            analysis = self.analyze_single_image(input_data)
        else:
            # URL but unknown type - try as video first
            try:
                frames = self.download_and_extract(input_data)
                analysis = self.analyze_video_frames(frames)
            except:
                analysis = self.analyze_description(input_data)
    elif os.path.isfile(input_data):
        if self._looks_like_video(input_data):
            frames = self._extract_frames_local(input_data)
            analysis = self.analyze_video_frames(frames)
        else:
            analysis = self.analyze_single_image(input_data)
    else:
        # Treat as text description
        analysis = self.analyze_description(input_data)
    
    # Generate code
    result = self.generate_code(analysis, content)
    
    return {
        "analysis_metadata": self._metadata(analysis),
        "css": result["css"],
        "jsx": result["jsx"],
        "npm_packages": result["npm_packages"],
        "components": result["components"],
        "technology_stack": result["technology_stack"]
    }
```

---

## ALSO FIX THIS SYNTAX ERROR

In line 64, there's a missing closing parenthesis:

**BEFORE (WRONG):**
```python
content = context.get("content") if isinstance(context.get("content"), dict) else None
```

**AFTER (CORRECT):**
```python
content = context.get("content") if isinstance(context.get("content"), dict) else None
```

Wait, that looks the same. Check the original - ensure proper syntax.

---

## VERIFICATION CHECKLIST

After implementing, verify:

- [ ] `generate_code()` returns valid dict with keys: css, jsx, npm_packages, components, technology_stack
- [ ] Each `_generate_*` method returns a string
- [ ] All strings are properly formatted JSX/CSS
- [ ] `build_from_input()` exists and is callable
- [ ] No syntax errors in any method

---

## TEST CODE

Add this test to verify:

```python
def test_cinematic_generation():
    skill = CinematicDesign()
    
    # Test 1: Description input
    result = skill.build_from_input("dark cinematic hero with 3d rotating product")
    assert "css" in result
    assert "jsx" in result
    assert "npm_packages" in result
    assert result["technology_stack"]["animation"] in ["gsap", "framer_motion", "css_animation"]
    
    # Test 2: Check GSAP is detected for dark
    assert result["technology_stack"]["animation"] == "gsap"  # Dark theme → GSAP
    
    print("All tests passed!")
    print(f"Technology stack: {result['technology_stack']}")
    print(f"NPM packages: {result['npm_packages']}")
```

---

## FINAL REMINDER

1. Add `generate_code()` method
2. Add ALL 16 `_generate_*` sub-methods  
3. Add `build_from_input()` method
4. Fix any syntax errors
5. Test thoroughly

Missing ANY method = INCOMPLETE implementation.
