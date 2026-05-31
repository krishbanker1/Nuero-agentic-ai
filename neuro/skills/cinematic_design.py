"""Cinematic design intelligence for premium web/app/presentation visuals.

The skill is free-first and keeps visual-analysis dependencies optional. Text
analysis and CSS/JS generation work with the standard library; video/image
analysis activates only when the user installs the optional visual packages.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


class CinematicDesign:
    """Analyze visual inputs and generate derived cinematic UI effects."""

    NAME = "cinematic_design"
    DESCRIPTION = "Analyze visual content and generate premium cinematic web/app/presentations"
    TRIGGERS = [
        "cinematic", "premium", "3d effect", "dark theme", "motion graphics",
        "hero section", "gradient", "spotlight", "animation", "web design",
        "landing page", "premium website", "analyze", "extract from video",
        "build from reference", "visual analysis", "design system",
    ]
    REQUIRED_PACKAGES = ["yt-dlp", "opencv-python", "Pillow", "numpy", "requests"]
    TECHNOLOGY_STACKS = {
        "animation_libraries": {
            "gsap": {"npm": "gsap", "features": ["timeline", "scrolltrigger", "easings"]},
            "framer_motion": {"npm": "framer-motion", "features": ["variants", "gestures", "layout"]},
            "react_spring": {"npm": "@react-spring/web", "features": ["spring physics", "trail", "decay"]},
            "motion_one": {"npm": "motion", "features": ["timeline", "scroll", "keyframes"]},
            "css_animation": {"npm": None, "features": ["@keyframes", "transitions", "transforms"]},
        },
        "3d_libraries": {
            "threejs": {"npm": "three @react-three/fiber @react-three/drei", "features": ["mesh", "lighting", "materials"]},
            "babylonjs": {"npm": "@babylonjs/core @babylonjs/loaders", "features": ["scene", "engine", "physics"]},
            "css_3d": {"npm": None, "features": ["perspective", "rotateY", "translateZ"]},
        },
        "text_animation": {
            "split_type": {"npm": "split-type", "features": ["chars", "words", "lines"]},
            "blotter": {"npm": "blotter", "features": ["procedural text", "shader text"]},
            "css_text": {"npm": None, "features": ["clip-path", "mask", "transform"]},
        },
        "scroll_libraries": {
            "lenis": {"npm": "lenis", "features": ["smooth scroll", "lerp"]},
            "locomotive_scroll": {"npm": "locomotive-scroll", "features": ["parallax", "sticky", "sections"]},
            "gsap_scroll": {"npm": "gsap", "features": ["scrub", "pin", "snap"]},
            "native_scroll": {"npm": None, "features": ["IntersectionObserver", "CSS scroll-behavior"]},
        },
    }

    @classmethod
    def invoke(cls, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """SkillOrchestrator-compatible entry point."""
        context = context or {}
        skill = cls()
        source = context.get("source") or context.get("url") or task
        content = context.get("content") if isinstance(context.get("content"), dict) else None
        component = skill.build_from_input(source, content)
        return {
            "capabilities": [
                "derive cinematic design tokens from text, image, or video inputs",
                "generate premium 3D depth, dark cinematic, gradient, and motion CSS",
                "produce React/Framer Motion hero component snippets without changing model routing",
            ],
            "cinematic_analysis": component["analysis_metadata"],
            "cinematic_component": component,
            "cinematic_prompt": skill.build_prompt_block(component),
            "prompt_block": skill.build_prompt_block(component),
            "requires_paid_service": False,
        }

    def download_and_extract(self, url: str) -> list[dict[str, Any]]:
        """Download any supported video URL with yt-dlp and extract RGB frames."""
        yt_dlp, cv2, image_cls, _np = self._load_video_dependencies()
        frames: list[dict[str, Any]] = []
        temp_dir = tempfile.mkdtemp(prefix="cinematic_")
        try:
            ydl_opts = {
                "format": "best[ext=mp4]/best",
                "outtmpl": os.path.join(temp_dir, "video.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = self._find_downloaded_video(temp_dir, info)
            frames = self._extract_frames(video_path, temp_dir, cv2=cv2, image_cls=image_cls)
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
        return frames

    def _find_downloaded_video(self, temp_dir: str, info: dict[str, Any]) -> str:
        """Find the downloaded media file without platform-specific assumptions."""
        ext = info.get("ext", "mp4")
        candidates = [os.path.join(temp_dir, f"video.{ext}"), os.path.join(temp_dir, "video.mp4")]
        for path in candidates:
            if os.path.exists(path):
                return path
        for filename in os.listdir(temp_dir):
            suffix = filename.rsplit(".", 1)[-1].lower()
            if filename.startswith("video.") and suffix in {"mp4", "webm", "mov", "avi", "mkv", "m4v"}:
                return os.path.join(temp_dir, filename)
        raise FileNotFoundError("Video download failed")

    def _extract_frames(
        self,
        video_path: str,
        temp_dir: str,
        fps_multiplier: float = 0.5,
        cv2: Any | None = None,
        image_cls: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Extract frames at temporal intervals using OpenCV when installed."""
        if cv2 is None or image_cls is None:
            _yt_dlp, cv2, image_cls, _np = self._load_video_dependencies()
        frames: list[dict[str, Any]] = []
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 1
        frame_interval = max(1, int(fps * fps_multiplier))
        frame_idx = 0
        saved_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                timestamp = frame_idx / fps
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_path = os.path.join(temp_dir, f"frame_{saved_idx:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append({
                    "frame_index": saved_idx,
                    "timestamp": float(timestamp),
                    "image_path": frame_path,
                    "numpy_array": frame_rgb,
                    "pil_image": image_cls.fromarray(frame_rgb),
                })
                saved_idx += 1
            frame_idx += 1
        cap.release()
        return frames

    def analyze_single_image(self, source: str) -> dict[str, Any]:
        """Analyze a local or URL image when Pillow/numpy are available."""
        image_cls, np = self._load_image_dependencies()
        path = self._download_image(source) if self._looks_like_url(source) else source
        with image_cls.open(path) as image:
            rgb_image = image.convert("RGB").resize((min(image.width, 320), min(image.height, 320)))
            return self._analyze_image_array(np.asarray(rgb_image))

    def analyze_video_frames(self, frames: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze extracted video frames for temporal design metrics."""
        if not frames:
            return self._default_analysis()
        np = self._load_numpy()
        brightness_values: list[float] = []
        edge_scores: list[float] = []
        saturation_values: list[float] = []
        motion_scores: list[float] = []
        motion_timeline: list[float] = []
        for index, frame_data in enumerate(frames):
            frame = frame_data["numpy_array"]
            frame_analysis = self._analyze_image_array(frame)
            brightness_values.append(frame_analysis["brightness_mean"])
            edge_scores.append(frame_analysis["edge_score"])
            saturation_values.append(frame_analysis["saturation_mean"])
            if index > 0:
                prev_frame = frames[index - 1]["numpy_array"].astype(float)
                curr_frame = frame.astype(float)
                motion = float(np.abs(curr_frame - prev_frame).mean() * 10)
                motion_scores.append(motion)
                motion_timeline.append(motion)
        avg_brightness = float(np.mean(brightness_values))
        avg_edge = float(np.mean(edge_scores))
        avg_saturation = float(np.mean(saturation_values))
        avg_motion = float(np.mean(motion_scores)) if motion_scores else 0.0
        scene_changes, scene_timestamps = self._detect_scene_changes(frames)
        brightness_range = (float(min(brightness_values)), float(max(brightness_values)))
        return self._finalize_analysis(
            avg_brightness=avg_brightness,
            avg_edge=avg_edge,
            avg_saturation=avg_saturation,
            brightness_std=float(np.std(brightness_values)),
            motion_score=avg_motion,
            color_palette=self._merge_frame_colors(frames[:10]),
            lighting_type=self._detect_lighting(frames[0]["numpy_array"]),
            scene_changes=scene_changes,
            scene_change_timestamps=scene_timestamps,
            frame_count=len(frames),
            duration_seconds=float(frames[-1].get("timestamp", 0.0)),
            brightness_range=brightness_range,
            motion_timeline=motion_timeline,
        )

    def analyze_description(self, text: str) -> dict[str, Any]:
        """Derive cinematic design metrics from natural language."""
        tokens = set(re.findall(r"[\w-]+", text.lower()))
        dark_score = self._score(tokens, {"dark", "night", "premium", "luxury", "dramatic", "gaming", "moody", "shadow", "black", "deep", "midnight", "neon"})
        bright_score = self._score(tokens, {"light", "clean", "minimal", "white", "bright", "airy", "fresh", "soft", "pastel", "transparent"})
        depth_score = self._score(tokens, {"3d", "depth", "product", "rotate", "layered", "dimensional", "perspective", "parallax"})
        flat_score = self._score(tokens, {"2d", "flat", "simple", "minimal", "clean", "basic", "plain"})
        heavy_score = self._score(tokens, {"animated", "motion", "dynamic", "fast", "loop", "continuous", "active", "energetic", "vibrant"})
        subtle_score = self._score(tokens, {"smooth", "gentle", "subtle", "fade", "transition", "ease", "soft", "calm", "flowing"})
        saturation_score = self._score(tokens, {"vibrant", "saturated", "bold", "colorful", "bright", "vivid", "intense", "striking"})
        muted_score = self._score(tokens, {"muted", "pastel", "neutral", "grayscale", "monochrome", "subtle", "minimal"})
        brightness = 45.0 if dark_score > bright_score else 190.0 if bright_score > dark_score else 110.0
        edge_score = 250.0 if depth_score > flat_score else 30.0 if flat_score > 0 else 100.0
        motion_score = 15.0 if heavy_score > subtle_score else 5.0 if subtle_score > 0 else 0.0
        saturation = 190.0 if saturation_score > muted_score else 55.0 if muted_score > saturation_score else 110.0
        color_palette = self._palette_from_text(tokens, brightness, saturation)
        return self._finalize_analysis(
            avg_brightness=brightness,
            avg_edge=edge_score,
            avg_saturation=saturation,
            brightness_std=45.0 if "contrast" in tokens or "dramatic" in tokens else 20.0,
            motion_score=motion_score,
            color_palette=color_palette,
            lighting_type="spotlight" if {"spotlight", "hero", "product"} & tokens else "dramatic" if "dramatic" in tokens else "ambient",
            scene_changes=0,
            scene_change_timestamps=[],
            frame_count=0,
            duration_seconds=0.0,
            brightness_range=(max(0.0, brightness - 35), min(255.0, brightness + 35)),
            motion_timeline=[],
        )

    def analyze_input(self, input_data: str) -> dict[str, Any]:
        """Route URL/path/description to the best available analyzer."""
        if not input_data:
            return self._default_analysis()
        if os.path.exists(input_data):
            return self._analyze_local_file(input_data)
        if self._looks_like_url(input_data):
            if self._looks_like_image(input_data):
                return self._safe_visual_call(lambda: self.analyze_single_image(input_data), input_data)
            if self._looks_like_video(input_data) or "." in input_data:
                return self._safe_visual_call(lambda: self.analyze_video_frames(self.download_and_extract(input_data)), input_data)
        return self.analyze_description(input_data)

    def generate_3d_depth(self, params: dict[str, Any]) -> str:
        """Generate 3D depth CSS from measured/derived analysis values."""
        edge_score = float(params.get("edge_score", 100))
        depth_perception = params.get("depth_perception", "2.5d")
        motion_level = params.get("motion_level", "static")
        lighting = params.get("lighting_type", "ambient")
        perspective = min(2000, max(500, int(edge_score * 10)))
        rotation_range = 45 if depth_perception == "3d" else 20 if depth_perception == "2.5d" else 10
        duration = 4 if motion_level == "heavy" else 8 if motion_level == "subtle" else 6
        spotlight_opacity = 0.5 if lighting == "spotlight" else 0.3 if lighting == "dramatic" else 0.2
        spotlight_size = 250 if lighting == "spotlight" else 300 if lighting == "dramatic" else 400
        return f"""
/* 3D depth derived from edge_score: {edge_score:.2f} */
.cinematic-3d {{
  transform-style: preserve-3d;
  perspective: {perspective}px;
}}

@keyframes rotate-3d {{
  0%, 100% {{ transform: rotateY(0deg) rotateX(0deg); }}
  25% {{ transform: rotateY({rotation_range}deg) rotateX({rotation_range // 4}deg); }}
  75% {{ transform: rotateY(-{rotation_range}deg) rotateX(-{rotation_range // 4}deg); }}
}}

.cinematic-3d-element {{
  animation: rotate-3d {duration}s ease-in-out infinite;
  backface-visibility: hidden;
}}

.spotlight {{
  position: absolute;
  inset: 0;
  background: radial-gradient(circle {spotlight_size}px at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255,255,255,{spotlight_opacity}), transparent 70%);
  pointer-events: none;
}}

.depth-shadow {{
  box-shadow: 0 {10 + int(edge_score // 20)}px {20 + int(edge_score // 10)}px rgba(0,0,0,{0.2 + edge_score / 1000:.3f});
}}
"""

    def generate_dark_cinematic(self, params: dict[str, Any]) -> str:
        saturation = params.get("saturation", "medium")
        contrast = params.get("contrast", "medium")
        palette = params.get("color_palette", ["#0a0a0f", "#e94560"])
        sat_filter = 150 if saturation == "high" else 80 if saturation == "muted" else 100
        accent_opacity = 1.0 if saturation == "high" else 0.7 if saturation == "muted" else 0.85
        vignette_intensity = 0.7 if contrast == "high" else 0.4 if contrast == "low" else 0.55
        shadow_depth = 0.9 if contrast == "high" else 0.5 if contrast == "low" else 0.7
        accent = palette[1] if len(palette) > 1 else "#e94560"
        return f"""
/* Dark cinematic derived from saturation: {saturation}, contrast: {contrast} */
.dark-cinematic {{ background: #0a0a0f; position: relative; overflow: hidden; }}
.dark-cinematic::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.2) 40%, rgba(0,0,0,{shadow_depth}) 100%);
  pointer-events: none;
}}
.text-zone {{ background: linear-gradient(to top, rgba(0,0,0,0.95), rgba(0,0,0,{shadow_depth * 0.6:.2f}), transparent); }}
.accent-saturated {{ filter: saturate({sat_filter}%); opacity: {accent_opacity}; }}
.vignette {{ box-shadow: inset 0 0 {int(150 * vignette_intensity)}px rgba(0,0,0,{vignette_intensity}); }}
.accent-glow {{ box-shadow: 0 0 20px {accent}40, 0 0 40px {accent}20; }}
"""

    def generate_gradient(self, params: dict[str, Any]) -> str:
        brightness_range = params.get("brightness_range", (50, 200))
        palette = params.get("color_palette", ["#ffffff", "#000000"])
        top_brightness = float(brightness_range[0])
        top_color = self._brightness_to_rgb(min(top_brightness, 100))
        mid_color = palette[1] if len(palette) >= 2 else "rgba(128,128,128,0.5)"
        return f"""
.gradient-depth {{
  background: linear-gradient(to bottom, {top_color} 0%, {mid_color} 42%, #000000 100%);
}}
.radial-spotlight {{ background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.6) 100%); }}
.gradient-overlay {{ background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.4) 100%); }}
"""

    def generate_motion(self, params: dict[str, Any]) -> str:
        motion_level = params.get("motion_level", "static")
        duration = 0.4 if motion_level == "heavy" else 0.7 if motion_level == "subtle" else 0.5
        stagger_delay = 0.08 if motion_level == "heavy" else 0.15 if motion_level == "subtle" else 0.12
        slide_distance = 60 if motion_level == "heavy" else 30 if motion_level == "subtle" else 40
        scale_start = 0.9 if motion_level == "heavy" else 0.97 if motion_level == "subtle" else 0.95
        return f"""
@keyframes fade-up {{
  from {{ opacity: 0; transform: translateY({slide_distance}px) scale({scale_start}); }}
  to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.stagger-container > * {{ animation: fade-up {duration}s ease-out forwards; }}
.stagger-container > *:nth-child(1) {{ animation-delay: 0s; }}
.stagger-container > *:nth-child(2) {{ animation-delay: {stagger_delay}s; }}
.stagger-container > *:nth-child(3) {{ animation-delay: {stagger_delay * 2:.2f}s; }}
.hover-lift {{ transition: transform {duration}s ease-out, box-shadow {duration}s ease-out; }}
.hover-lift:hover {{ transform: translateY(-5px) scale(1.02); box-shadow: 0 20px 40px rgba(0,0,0,0.2); }}
.reveal-on-scroll {{ opacity: 0; transform: translateY({slide_distance}px); transition: opacity {duration}s ease-out, transform {duration}s ease-out; }}
.reveal-on-scroll.visible {{ opacity: 1; transform: translateY(0); }}
"""

    def generate_framer_motion(self, params: dict[str, Any]) -> str:
        motion_level = params.get("motion_level", "static")
        stagger = 0.08 if motion_level == "heavy" else 0.2 if motion_level == "subtle" else 0.15
        stiffness = 120 if motion_level == "heavy" else 60 if motion_level == "subtle" else 80
        damping = 12 if motion_level == "heavy" else 20 if motion_level == "subtle" else 15
        y_start = 60 if motion_level == "heavy" else 30 if motion_level == "subtle" else 50
        return f"""
import {{ motion }} from 'framer-motion';
import {{ useEffect, useState }} from 'react';

const containerVariants = {{
  hidden: {{ opacity: 0 }},
  visible: {{ opacity: 1, transition: {{ staggerChildren: {stagger} }} }},
}};
const itemVariants = {{
  hidden: {{ opacity: 0, y: {y_start} }},
  visible: {{ opacity: 1, y: 0, transition: {{ type: 'spring', stiffness: {stiffness}, damping: {damping} }} }},
}};

export default function CinematicHero({{ content }}) {{
  const [mousePos, setMousePos] = useState({{ x: 50, y: 50 }});
  useEffect(() => {{
    const handleMouse = (event) => setMousePos({{ x: (event.clientX / window.innerWidth) * 100, y: (event.clientY / window.innerHeight) * 100 }});
    window.addEventListener('mousemove', handleMouse);
    return () => window.removeEventListener('mousemove', handleMouse);
  }}, []);
  return (
    <section className="cinematic-hero dark-cinematic cinematic-3d" style={{{{ '--mouse-x': `${{mousePos.x}}%`, '--mouse-y': `${{mousePos.y}}%` }}}}>
      <motion.div className="hero-content stagger-container" variants={{containerVariants}} initial="hidden" animate="visible">
        <motion.h1 className="hero-title" variants={{itemVariants}}>{{content?.title ?? 'Premium Headline'}}</motion.h1>
        <motion.p className="hero-subtitle" variants={{itemVariants}}>{{content?.subtitle ?? 'Cinematic experience'}}</motion.p>
        <motion.button className="hero-cta hover-lift accent-saturated" variants={{itemVariants}} whileHover={{{{ scale: 1.05 }}}} whileTap={{{{ scale: 0.95 }}}}>{{content?.cta ?? 'Explore'}}</motion.button>
      </motion.div>
      <div className="spotlight" />
    </section>
  );
}}
"""

    def generate_complete_component(self, analysis: dict[str, Any], content: dict[str, str]) -> dict[str, Any]:
        patterns_used: list[str] = []
        css_parts: list[str] = []
        jsx_parts: list[str] = []
        patterns = analysis.get("patterns_needed", [])
        if "3d_depth" in patterns:
            css_parts.append(self.generate_3d_depth(analysis))
            patterns_used.append("3d_depth")
        if "dark_cinematic" in patterns:
            css_parts.append(self.generate_dark_cinematic(analysis))
            patterns_used.append("dark_cinematic")
        if "gradient" in patterns:
            css_parts.append(self.generate_gradient(analysis))
            patterns_used.append("gradient")
        if "motion" in patterns:
            css_parts.append(self.generate_motion(analysis))
            jsx_parts.append(self.generate_framer_motion(analysis))
            patterns_used.append("motion")
        tech_stack = self.detect_technology_stack(analysis)
        library_code = self.generate_library_implementation(analysis, tech_stack)
        packages = sorted(set(library_code.pop("packages", []) + tech_stack.get("recommended_packages", [])))
        return {
            "css": "\n\n".join(css_parts),
            "jsx": jsx_parts[0] if jsx_parts else self._generate_basic_jsx(content),
            "component_name": "CinematicHero",
            "patterns_used": patterns_used,
            "analysis_metadata": self._metadata(analysis),
            "technology_stack": tech_stack,
            "library_code": library_code,
            "packages": packages,
        }

    def detect_technology_stack(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Detect animation/3D/text/scroll libraries from derived analysis."""
        brightness = analysis.get("brightness_level", "medium")
        motion = analysis.get("motion_level", "static")
        depth = analysis.get("depth_perception", "2d")
        edge_score = float(analysis.get("edge_score", 50))
        scene_changes = int(analysis.get("scene_changes", 0))
        packages: list[str] = []
        reasoning: dict[str, str] = {}

        if motion == "heavy" or brightness == "dark":
            animation = "gsap"
            packages.append("gsap")
            reasoning["animation"] = "Heavy or dark cinematic motion benefits from timeline control."
        elif motion == "subtle":
            animation = "framer_motion"
            packages.append("framer-motion")
            reasoning["animation"] = "Subtle React motion benefits from declarative variants."
        else:
            animation = "css_animation"
            reasoning["animation"] = "Static/simple motion can remain dependency-free."

        if depth == "3d" and edge_score > 220:
            three_d = "threejs"
            packages.extend(["three", "@react-three/fiber", "@react-three/drei"])
            reasoning["3d"] = "High edge score indicates real 3D/object depth."
        elif depth == "3d" and edge_score > 150:
            three_d = "babylonjs"
            packages.extend(["@babylonjs/core", "@babylonjs/loaders"])
            reasoning["3d"] = "Complex 3D depth can use Babylon.js enterprise tooling."
        elif depth in {"2.5d", "3d"}:
            three_d = "css_3d"
            reasoning["3d"] = "Moderate depth can use CSS transforms without WebGL."
        else:
            three_d = None
            reasoning["3d"] = "Flat visuals do not need a 3D runtime."

        if brightness == "dark":
            text_animation = "split_type"
            packages.append("split-type")
            reasoning["text"] = "Dark cinematic typography benefits from split text reveals."
        elif motion == "heavy" and edge_score > 150:
            text_animation = "blotter"
            packages.append("blotter")
            reasoning["text"] = "Complex motion/depth can support procedural text effects."
        else:
            text_animation = "css_text"
            reasoning["text"] = "Simple text animation can stay CSS-only."

        if scene_changes > 2:
            scroll = "locomotive_scroll"
            packages.append("locomotive-scroll")
            reasoning["scroll"] = "Multiple scene changes suggest section/parallax scrolling."
        elif animation == "gsap":
            scroll = "gsap_scroll"
            reasoning["scroll"] = "GSAP timeline can reuse ScrollTrigger for scroll motion."
        elif motion == "subtle":
            scroll = "lenis"
            packages.append("lenis")
            reasoning["scroll"] = "Subtle premium motion benefits from smooth scrolling."
        else:
            scroll = "native_scroll"
            reasoning["scroll"] = "Native scroll keeps the dependency budget small."

        return {
            "animation_library": animation,
            "3d_library": three_d,
            "text_animation": text_animation,
            "scroll_effect": scroll,
            "recommended_packages": sorted(set(packages)),
            "reasoning": reasoning,
        }

    def generate_library_implementation(self, analysis: dict[str, Any], stack: dict[str, Any]) -> dict[str, Any]:
        """Generate implementation snippets for the detected library stack."""
        result: dict[str, Any] = {"imports": [], "packages": []}
        animation = stack.get("animation_library")
        if animation == "gsap":
            result["animation_code"] = self._generate_gsap(analysis)
            result["imports"].append("import gsap from 'gsap'")
            result["packages"].append("gsap")
        elif animation == "framer_motion":
            result["animation_code"] = self.generate_framer_motion(analysis)
            result["imports"].append("import { motion } from 'framer-motion'")
            result["packages"].append("framer-motion")
        elif animation == "react_spring":
            result["animation_code"] = self._generate_react_spring(analysis)
            result["imports"].append("import { animated, useSpring } from '@react-spring/web'")
            result["packages"].append("@react-spring/web")
        elif animation == "motion_one":
            result["animation_code"] = self._generate_motion_one(analysis)
            result["imports"].append("import { animate, scroll } from 'motion'")
            result["packages"].append("motion")
        else:
            result["animation_code"] = self.generate_motion(analysis)

        three_d = stack.get("3d_library")
        if three_d == "threejs":
            result["3d_code"] = self._generate_threejs(analysis)
            result["imports"].append("import * as THREE from 'three'")
            result["packages"].extend(["three", "@react-three/fiber", "@react-three/drei"])
        elif three_d == "babylonjs":
            result["3d_code"] = self._generate_babylonjs(analysis)
            result["imports"].extend(["import * as BABYLON from '@babylonjs/core'", "import '@babylonjs/loaders'"])
            result["packages"].extend(["@babylonjs/core", "@babylonjs/loaders"])
        elif three_d == "css_3d":
            result["3d_code"] = self.generate_3d_depth(analysis)

        if stack.get("text_animation") == "blotter":
            result["text_code"] = self._generate_blotter(analysis)
            result["imports"].append("import Blotter from 'blotter'")
            result["packages"].append("blotter")
        elif stack.get("text_animation") == "split_type":
            result["text_code"] = self._generate_split_type(analysis)
            result["imports"].append("import SplitType from 'split-type'")
            result["packages"].append("split-type")
        else:
            result["text_code"] = ".text-reveal { clip-path: inset(0 0 0 0); transition: clip-path .7s ease; }"

        if stack.get("scroll_effect") == "locomotive_scroll":
            result["scroll_code"] = self._generate_locomotive(analysis)
            result["imports"].append("import LocomotiveScroll from 'locomotive-scroll'")
            result["packages"].append("locomotive-scroll")
        elif stack.get("scroll_effect") == "gsap_scroll":
            result["scroll_code"] = self._generate_gsap_scroll(analysis)
            result["packages"].append("gsap")
        elif stack.get("scroll_effect") == "lenis":
            result["scroll_code"] = self._generate_lenis(analysis)
            result["imports"].append("import Lenis from 'lenis'")
            result["packages"].append("lenis")
        else:
            result["scroll_code"] = "const observer = new IntersectionObserver(entries => entries.forEach(entry => entry.target.classList.toggle('visible', entry.isIntersecting)));"
        return result


    def generate_code(self, analysis: dict[str, Any], content: dict[str, str] | None = None) -> dict[str, Any]:
        """Generate complete, working CSS/JSX snippets for the detected stack.

        This is the direct code-generation API requested by the cinematic
        prompt. It keeps outputs dependency-aware and free-first by only adding
        npm packages for libraries that the detected stack actually needs.
        """
        content = content or {"title": "Premium", "subtitle": "Cinematic", "cta": "Explore"}
        tech_stack = self.detect_technology_stack(analysis)

        anim = tech_stack.get("animation_library") or "css_animation"
        three_d = tech_stack.get("3d_library")
        text_anim = tech_stack.get("text_animation")
        scroll = tech_stack.get("scroll_effect")

        packages: list[str] = []
        css_parts: list[str] = []
        jsx_parts: list[str] = []
        components: list[str] = []

        if anim == "gsap":
            css_parts.append(self._generate_gsap_css(analysis))
            jsx_parts.append(self._generate_gsap_jsx())
            packages.append("gsap")
            components.append("GSAPAnimation")
        elif anim == "framer_motion":
            css_parts.append(self._generate_framer_css(analysis))
            jsx_parts.append(self._generate_framer_jsx())
            packages.append("framer-motion")
            components.append("FramerHero")
        else:
            css_parts.append(self._generate_css_animation(analysis))
            jsx_parts.append(self._generate_basic_jsx(content))
            components.append("CSSHero")

        if three_d == "threejs":
            css_parts.append(self._generate_threejs_css())
            jsx_parts.append(self._generate_threejs_jsx(analysis))
            packages.extend(["three", "@react-three/fiber", "@react-three/drei"])
            components.append("ThreeScene")
        elif three_d == "babylonjs":
            css_parts.append(self._generate_babylonjs_css())
            jsx_parts.append(self._generate_babylonjs_jsx(analysis))
            packages.extend(["@babylonjs/core", "@babylonjs/loaders"])
            components.append("BabylonScene")
        elif three_d == "css_3d":
            css_parts.append(self._generate_css_3d(analysis))

        if text_anim == "split_type":
            jsx_parts.append(self._generate_splittext_jsx())
            packages.append("split-type")
            components.append("SplitText")
        elif text_anim == "blotter":
            jsx_parts.append(self._generate_blotter_jsx())
            packages.append("blotter")
            components.append("BlotterText")

        if scroll == "lenis":
            css_parts.append(self._generate_lenis_css())
            jsx_parts.append(self._generate_lenis_jsx())
            packages.append("lenis")
            components.append("LenisProvider")
        elif scroll == "locomotive_scroll":
            css_parts.append(self._generate_locomotive_css())
            jsx_parts.append(self._generate_locomotive_jsx())
            packages.append("locomotive-scroll")
            components.append("LocomotiveProvider")
        elif scroll == "gsap_scroll":
            packages.append("gsap")

        stack_info = {
            "animation": anim,
            "3d": three_d,
            "text": text_anim,
            "scroll": scroll,
            "animation_library": anim,
            "3d_library": three_d,
            "text_animation": text_anim,
            "scroll_effect": scroll,
            "reasoning": tech_stack.get("reasoning", {}),
        }
        return {
            "css": "\n\n".join(part.strip() for part in css_parts if part and part.strip()),
            "jsx": "\n\n".join(part.strip() for part in jsx_parts if part and part.strip()),
            "npm_packages": sorted(set(packages)),
            "components": components,
            "technology_stack": stack_info,
        }

    def _generate_gsap_css(self, analysis: dict[str, Any]) -> str:
        """Generate GSAP-compatible CSS classes."""
        motion = analysis.get("motion_level", "subtle")
        duration = "0.4" if motion == "heavy" else "0.6"
        stagger = "0.05" if motion == "heavy" else "0.15"
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

.gsap-hero {{ position: relative; overflow: hidden; min-height: 100vh; display: grid; place-items: center; }}
.gsap-title {{ animation: fade-up {duration}s ease-out forwards; }}
.gsap-subtitle {{ animation: fade-up {duration}s ease-out {float(stagger)}s forwards; opacity: 0; }}
.gsap-cta {{ animation: scale-in {duration}s ease-out {float(stagger) * 2}s forwards; opacity: 0; }}
.scroll-indicator {{ animation: bounce 2s infinite; }}
@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(10px); }}
}}
"""

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

    def _generate_framer_css(self, analysis: dict[str, Any]) -> str:
        return """
/* Framer Motion Animations */
.framer-hero { position: relative; overflow: hidden; min-height: 100vh; display: grid; place-items: center; }
.framer-title, .framer-subtitle, .framer-cta { will-change: transform, opacity; }
"""

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

    def _generate_css_animation(self, analysis: dict[str, Any]) -> str:
        motion = analysis.get("motion_level", "subtle")
        duration = "0.5s" if motion == "subtle" else "0.3s"
        return f"""
/* CSS Animation Hero */
@keyframes fade-up {{
  from {{ opacity: 0; transform: translateY(40px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.css-hero {{ position: relative; min-height: 100vh; display: grid; place-items: center; }}
.css-hero h1 {{ animation: fade-up {duration} ease-out forwards; }}
.css-hero p {{ animation: fade-up {duration} ease-out 0.2s forwards; opacity: 0; }}
.css-hero button {{ animation: fade-up {duration} ease-out 0.4s forwards; opacity: 0; }}
"""

    def _generate_threejs_css(self) -> str:
        return """
/* Three.js Scene */
.three-canvas { width: 100%; height: 100vh; position: absolute; top: 0; left: 0; z-index: 0; }
.three-content { position: relative; z-index: 1; }
"""

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
    <div className="three-canvas">
      <Canvas camera={{{{ position: [0, 0, 5], fov: 45 }}}}>
{lights.rstrip()}
        <mesh>
          <sphereGeometry args={{[1, 32, 32]}} />
          <meshStandardMaterial color="#8a2be2" metalness={{0.8}} roughness={{0.2}} />
        </mesh>
        <Environment preset="city" />
        <OrbitControls enableZoom={{false}} autoRotate autoRotateSpeed={{0.5}} />
      </Canvas>
    </div>
  )
}}
"""

    def _generate_babylonjs_css(self) -> str:
        return """
/* Babylon.js Scene */
.babylon-canvas { width: 100%; height: 100vh; display: block; }
.babylon-content { position: relative; z-index: 1; }
"""

    def _generate_babylonjs_jsx(self, analysis: dict[str, Any]) -> str:
        return """
export function BabylonScene({ canvasId }) {
  // Initialize in useEffect with:
  // const { Engine, Scene, ArcRotateCamera, HemisphericLight, Vector3, MeshBuilder } = await import('@babylonjs/core')
  return <canvas id={canvasId || 'babylon-canvas'} className="babylon-canvas" />
}
"""

    def _generate_css_3d(self, analysis: dict[str, Any]) -> str:
        edge = float(analysis.get("edge_score", 100))
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

    def _generate_blotter_jsx(self) -> str:
        return """
import { useEffect, useRef } from 'react'
import Blotter from 'blotter'

export function BlotterText({ text, className }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current) return
    const material = new Blotter.RollingDistortMaterial()
    const blotterText = new Blotter.Text(text, { size: 96 })
    const blotter = new Blotter(material, { texts: [blotterText] })
    const scope = blotter.forText(blotterText)
    scope.appendTo(ref.current)
    return () => { blotter.stop(); ref.current && (ref.current.innerHTML = '') }
  }, [text])

  return <div ref={ref} className={className} />
}
"""

    def _generate_lenis_css(self) -> str:
        return """
/* Lenis Smooth Scroll */
html.lenis { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto; }
[data-lenis-scroll] { transform: translateY(calc(var(--scroll, 0) * 1px)); }
"""

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

    def _generate_locomotive_css(self) -> str:
        return """
/* Locomotive Scroll */
[data-scroll-container] { perspective: 1px; overflow: hidden; }
[data-scroll] { will-change: transform; }
[data-scroll-speed="1"] { transform: translateY(calc(var(--scroll, 0) * 1px)); }
[data-scroll-speed="-1"] { transform: translateY(calc(var(--scroll, 0) * -1px)); }
"""

    def _generate_locomotive_jsx(self) -> str:
        return """
import { useEffect } from 'react'
import LocomotiveScroll from 'locomotive-scroll'

export function LocomotiveProvider({ children }) {
  useEffect(() => {
    const scroll = new LocomotiveScroll({ smooth: true })
    return () => scroll.destroy()
  }, [])

  return <div data-scroll-container>{children}</div>
}
"""

    def _generate_gsap(self, params: dict[str, Any]) -> str:
        duration = 0.8 if params.get("motion_level") == "heavy" else 1.2
        return f"""gsap.timeline({{ defaults: {{ ease: 'power3.out', duration: {duration} }} }})
  .from('.hero-title .char', {{ yPercent: 120, opacity: 0, stagger: 0.025 }})
  .from('.hero-subtitle', {{ y: 32, opacity: 0 }}, '-=0.35')
  .from('.hero-cta', {{ scale: 0.92, opacity: 0 }}, '-=0.25');"""

    def _generate_react_spring(self, params: dict[str, Any]) -> str:
        tension = 210 if params.get("motion_level") == "heavy" else 140
        return f"""const heroSpring = useSpring({{
  from: {{ opacity: 0, y: 40 }},
  to: {{ opacity: 1, y: 0 }},
  config: {{ tension: {tension}, friction: 22 }},
}});"""

    def _generate_motion_one(self, params: dict[str, Any]) -> str:
        distance = 48 if params.get("motion_level") == "heavy" else 24
        return f"""animate('.hero-title', {{ opacity: [0, 1], transform: ['translateY({distance}px)', 'translateY(0)'] }}, {{ duration: 0.8, easing: 'ease-out' }});
scroll(animate('.cinematic-hero', {{ transform: ['scale(1)', 'scale(1.04)'] }}));"""

    def _generate_threejs(self, params: dict[str, Any]) -> str:
        intensity = 1.4 if params.get("lighting_type") == "spotlight" else 0.9
        return f"""const scene = new THREE.Scene();
const keyLight = new THREE.SpotLight(0xffffff, {intensity});
keyLight.position.set(3, 4, 5);
scene.add(keyLight);
// Add product mesh/material using extracted palette and edge-derived depth."""

    def _generate_babylonjs(self, params: dict[str, Any]) -> str:
        contrast = params.get("contrast", "medium")
        return f"""const engine = new BABYLON.Engine(canvas, true);
const scene = new BABYLON.Scene(engine);
scene.environmentIntensity = {1.2 if contrast == 'high' else 0.8};
new BABYLON.ArcRotateCamera('camera', Math.PI / 2, Math.PI / 3, 5, BABYLON.Vector3.Zero(), scene);
new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);"""

    def _generate_blotter(self, params: dict[str, Any]) -> str:
        speed = 0.35 if params.get("motion_level") == "heavy" else 0.12
        return f"""const material = new Blotter.LiquidDistortMaterial();
material.uniforms.uSpeed.value = {speed};
const blotter = new Blotter(material, {{ texts: [new Blotter.Text('Premium', {{ size: 96 }})] }});"""

    def _generate_split_type(self, params: dict[str, Any]) -> str:
        stagger = 0.018 if params.get("motion_level") == "heavy" else 0.035
        return f"""const split = new SplitType('.hero-title', {{ types: 'chars, words' }});
gsap.from(split.chars, {{ yPercent: 120, opacity: 0, stagger: {stagger}, ease: 'power3.out' }});"""

    def _generate_locomotive(self, params: dict[str, Any]) -> str:
        lerp = 0.08 if params.get("motion_level") == "heavy" else 0.12
        return f"""const scroll = new LocomotiveScroll({{
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  lerp: {lerp},
}});"""

    def _generate_gsap_scroll(self, params: dict[str, Any]) -> str:
        scrub = "true" if params.get("motion_level") == "heavy" else "0.6"
        return f"""gsap.registerPlugin(ScrollTrigger);
gsap.to('.cinematic-hero', {{ scale: 1.04, scrollTrigger: {{ trigger: '.cinematic-hero', scrub: {scrub}, start: 'top top' }} }});"""

    def _generate_lenis(self, params: dict[str, Any]) -> str:
        lerp = 0.08 if params.get("motion_level") == "subtle" else 0.12
        return f"""const lenis = new Lenis({{ lerp: {lerp}, smoothWheel: true }});
function raf(time) {{ lenis.raf(time); requestAnimationFrame(raf); }}
requestAnimationFrame(raf);"""

    def build_from_input(self, input_data: str, content: dict[str, str] | None = None) -> dict[str, Any]:
        """Analyze input and return production-ready cinematic code artifacts."""
        content = content or {"title": "Premium Headline", "subtitle": "Subheadline text", "cta": "Explore"}
        analysis = self.analyze_input(input_data)
        component = self.generate_complete_component(analysis, content)
        generated = self.generate_code(analysis, content)
        component_css = "\n\n".join(part for part in [component.get("css", ""), generated["css"]] if part)
        component_jsx = "\n\n".join(part for part in [component.get("jsx", ""), generated["jsx"]] if part)
        component.update({
            "css": component_css,
            "jsx": component_jsx,
            "npm_packages": generated["npm_packages"],
            "packages": generated["npm_packages"],
            "components": generated["components"],
            "technology_stack": generated["technology_stack"],
        })
        return component

    def build_prompt_block(self, component: dict[str, Any]) -> str:
        patterns = ", ".join(component.get("patterns_used", [])) or "basic cinematic"
        metadata = component.get("analysis_metadata", {})
        stack = component.get("technology_stack", {})
        packages = ", ".join(component.get("packages", [])) or "no required packages"
        return (
            "Cinematic design intelligence active. Use measured/derived visual principles: "
            f"patterns={patterns}; brightness={metadata.get('brightness_level')}; "
            f"depth={metadata.get('depth_perception')}; motion={metadata.get('motion_level')}. "
            f"Detected stack: animation={stack.get('animation_library')}, 3d={stack.get('3d_library')}, "
            f"text={stack.get('text_animation')}, scroll={stack.get('scroll_effect')}. "
            f"Recommended packages: {packages}. "
            "Generate premium UI with complete CSS/React snippets and no paid services."
        )

    def _analyze_local_file(self, file_path: str) -> dict[str, Any]:
        ext = Path(file_path).suffix.lower()
        if ext in {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}:
            return self.analyze_video_frames(self._extract_frames(file_path, tempfile.mkdtemp(prefix="cinematic_local_")))
        if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
            return self.analyze_single_image(file_path)
        return self.analyze_description(Path(file_path).read_text(encoding="utf-8", errors="ignore")[:2000])

    def _safe_visual_call(self, func: Any, fallback_text: str) -> dict[str, Any]:
        try:
            return func()
        except Exception:
            return self.analyze_description(fallback_text)

    def _analyze_image_array(self, img_array: Any) -> dict[str, Any]:
        np = self._load_numpy()
        arr = img_array.astype(float)
        gray = arr.mean(axis=2)
        brightness_mean = float(gray.mean())
        brightness_std = float(gray.std())
        saturation_mean = float(self._rgb_to_hsv(arr / 255.0)[:, :, 1].mean() * 255)
        gy, gx = np.gradient(gray)
        edge_score = float(np.sqrt(gx * gx + gy * gy).mean() * 5)
        return self._finalize_analysis(
            avg_brightness=brightness_mean,
            avg_edge=edge_score,
            avg_saturation=saturation_mean,
            brightness_std=brightness_std,
            motion_score=0.0,
            color_palette=self._extract_colors(arr.astype("uint8")),
            lighting_type=self._detect_lighting(arr),
            scene_changes=0,
            scene_change_timestamps=[],
            frame_count=1,
            duration_seconds=0.0,
            brightness_range=(max(0.0, brightness_mean - brightness_std), min(255.0, brightness_mean + brightness_std)),
            motion_timeline=[],
        )

    def _finalize_analysis(
        self,
        *,
        avg_brightness: float,
        avg_edge: float,
        avg_saturation: float,
        brightness_std: float,
        motion_score: float,
        color_palette: list[str],
        lighting_type: str,
        scene_changes: int,
        scene_change_timestamps: list[float],
        frame_count: int,
        duration_seconds: float,
        brightness_range: tuple[float, float],
        motion_timeline: list[float],
    ) -> dict[str, Any]:
        brightness_level = "dark" if avg_brightness < 70 else "bright" if avg_brightness > 150 else "medium"
        depth_perception = "3d" if avg_edge > 200 else "2.5d" if avg_edge > 50 else "2d"
        saturation = "muted" if avg_saturation < 80 else "high" if avg_saturation > 150 else "medium"
        contrast = "high" if brightness_std > 50 else "medium" if brightness_std > 25 else "low"
        motion_level = "heavy" if motion_score > 10 else "subtle" if motion_score > 3 else "static"
        patterns = ["gradient"]
        if depth_perception in {"2.5d", "3d"}:
            patterns.append("3d_depth")
        if brightness_level == "dark":
            patterns.append("dark_cinematic")
        if motion_level != "static":
            patterns.append("motion")
        return {
            "brightness_level": brightness_level,
            "edge_score": float(avg_edge),
            "motion_level": motion_level,
            "motion_score": float(motion_score),
            "gradient_needed": True,
            "saturation": saturation,
            "contrast": contrast,
            "color_palette": color_palette or ["#0a0a0f", "#e94560", "#ffffff"],
            "patterns_needed": patterns,
            "lighting_type": lighting_type,
            "depth_perception": depth_perception,
            "scene_changes": scene_changes,
            "scene_change_timestamps": scene_change_timestamps,
            "frame_count": frame_count,
            "duration_seconds": duration_seconds,
            "avg_brightness": float(avg_brightness),
            "brightness_range": brightness_range,
            "motion_timeline": motion_timeline,
        }

    def _default_analysis(self) -> dict[str, Any]:
        return self.analyze_description("premium cinematic hero with subtle gradient and smooth depth")

    @staticmethod
    def _score(tokens: set[str], indicators: set[str]) -> int:
        return len(tokens & indicators)

    @staticmethod
    def _palette_from_text(tokens: set[str], brightness: float, saturation: float) -> list[str]:
        if brightness < 70 and saturation > 150:
            return ["#09090f", "#7c3aed", "#22d3ee", "#f8fafc"]
        if brightness < 70:
            return ["#0a0a0f", "#334155", "#94a3b8", "#ffffff"]
        if saturation > 150:
            return ["#f8fafc", "#2563eb", "#f97316", "#111827"]
        if "gold" in tokens or "luxury" in tokens:
            return ["#0b0b10", "#d4af37", "#fff8dc", "#1f2937"]
        return ["#111827", "#64748b", "#e2e8f0", "#ffffff"]

    @staticmethod
    def _brightness_to_rgb(value: float) -> str:
        channel = max(0, min(255, int(value * 2.55)))
        return f"rgb({channel}, {channel}, {channel})"

    @staticmethod
    def _looks_like_url(value: str) -> bool:
        return bool(re.match(r"https?://", value))

    @staticmethod
    def _looks_like_image(value: str) -> bool:
        return Path(value.split("?", 1)[0]).suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    @staticmethod
    def _looks_like_video(value: str) -> bool:
        return Path(value.split("?", 1)[0]).suffix.lower() in {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}

    @staticmethod
    def _metadata(analysis: dict[str, Any]) -> dict[str, Any]:
        keys = [
            "brightness_level", "edge_score", "motion_level", "motion_score", "saturation",
            "contrast", "lighting_type", "depth_perception", "color_palette", "scene_changes",
            "duration_seconds",
        ]
        return {key: analysis.get(key) for key in keys}

    @staticmethod
    def _generate_basic_jsx(content: dict[str, str]) -> str:
        return f"""
export default function CinematicHero() {{
  return (
    <section className="cinematic-hero gradient-depth">
      <h1 className="hero-title">{content.get('title', 'Premium Headline')}</h1>
      <p className="hero-subtitle">{content.get('subtitle', 'Subheadline text')}</p>
      <button className="hero-cta">{content.get('cta', 'Explore')}</button>
    </section>
  );
}}
"""

    def _detect_scene_changes(self, frames: list[dict[str, Any]], threshold: float = 50.0) -> tuple[int, list[float]]:
        np = self._load_numpy()
        changes = 0
        timestamps: list[float] = []
        for index in range(1, len(frames)):
            prev = frames[index - 1]["numpy_array"].astype(float)
            curr = frames[index]["numpy_array"].astype(float)
            if float(np.abs(curr - prev).mean()) > threshold:
                changes += 1
                timestamps.append(float(frames[index].get("timestamp", 0.0)))
        return changes, timestamps

    def _merge_frame_colors(self, frames: list[dict[str, Any]]) -> list[str]:
        colors: list[str] = []
        for frame in frames:
            colors.extend(self._extract_colors(frame["numpy_array"]))
        counts = Counter(colors)
        return [color for color, _count in counts.most_common(5)]

    def _extract_colors(self, img_array: Any, k: int = 5) -> list[str]:
        pixels = img_array.reshape(-1, 3)
        bins = 32
        quantized = (pixels // bins) * bins + bins // 2
        counts: Counter[tuple[int, int, int]] = Counter(tuple(int(v) for v in pixel) for pixel in quantized)
        return [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b), _count in counts.most_common(k)]

    def _detect_lighting(self, img_array: Any) -> str:
        np = self._load_numpy()
        gray = img_array.mean(axis=2)
        height, width = gray.shape[:2]
        center_h, center_w = max(1, height // 4), max(1, width // 4)
        center = gray[center_h:3 * center_h, center_w:3 * center_w]
        edges = np.concatenate([
            gray[:center_h, :].flatten(), gray[-center_h:, :].flatten(),
            gray[:, :center_w].flatten(), gray[:, -center_w:].flatten(),
        ])
        ratio = float(center.mean() / (edges.mean() + 1e-10))
        if ratio > 1.5:
            return "spotlight"
        if ratio < 0.7:
            return "dramatic"
        if float(np.std([center.mean(), edges.mean()])) < 10:
            return "soft"
        return "ambient"

    def _rgb_to_hsv(self, rgb: Any) -> Any:
        np = self._load_numpy()
        red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        maxc = np.maximum(np.maximum(red, green), blue)
        minc = np.minimum(np.minimum(red, green), blue)
        value = maxc
        saturation = (maxc - minc) / (maxc + 1e-10)
        saturation[maxc == 0] = 0
        delta = maxc - minc
        delta[maxc == 0] = 1
        hue = np.zeros_like(red)
        mask_r = maxc == red
        mask_g = (maxc == green) & ~mask_r
        mask_b = (maxc == blue) & ~(mask_r | mask_g)
        hue[mask_r] = ((green[mask_r] - blue[mask_r]) / delta[mask_r]) % 6
        hue[mask_g] = ((blue[mask_g] - red[mask_g]) / delta[mask_g]) + 2
        hue[mask_b] = ((red[mask_b] - green[mask_b]) / delta[mask_b]) + 4
        hue = hue / 6.0
        hue[hue < 0] += 1
        return np.stack([hue, saturation, value], axis=-1)

    @staticmethod
    def _download_image(url: str) -> str:
        tmp = tempfile.NamedTemporaryFile(prefix="cinematic_image_", suffix=Path(url).suffix or ".img", delete=False)
        tmp.close()
        with urllib.request.urlopen(url, timeout=20) as response:
            Path(tmp.name).write_bytes(response.read())
        return tmp.name

    @staticmethod
    def _load_numpy() -> Any:
        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("Install optional package numpy for image/video analysis") from exc
        return np

    def _load_image_dependencies(self) -> tuple[Any, Any]:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Install optional package Pillow for image analysis") from exc
        return Image, self._load_numpy()

    def _load_video_dependencies(self) -> tuple[Any, Any, Any, Any]:
        try:
            import cv2
            import yt_dlp
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Install optional packages yt-dlp, opencv-python, Pillow, and numpy for video analysis") from exc
        return yt_dlp, cv2, Image, self._load_numpy()


cinematic_design = CinematicDesign.invoke
