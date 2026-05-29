"""
Motion Graphics Suite - 3D, Animation, and Visual Effects
Enterprise-level UI/frontend design with motion and 3D graphics

FREE TOOLS:
- Three.js (3D WebGL)
- GSAP (Animations)
- Framer Motion (React)
- Lenis (Smooth scroll)
- React Spring (Physics)
- Motion One (Lightweight)
- Anime.js (General)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class MotionComponent:
    """Motion/graphics component."""
    name: str
    framework: str  # threejs, gsap, framer, etc.
    code: str
    description: str

class MotionGraphicsSuite:
    """
    Enterprise-level motion and 3D graphics for UI/frontend.
    All using free libraries (Three.js, GSAP, Framer Motion, etc.)
    
    Usage:
        from neuro.skills.motion_graphics_suite import MotionGraphicsSuite
        
        suite = MotionGraphicsSuite()
        component = suite.create_3d_hero("Modern, sleek hero section")
    """
    
    MODEL = "gemini/gemini-3.5-flash"  # Best for visual design
    
    def create_3d_hero(self, description: str) -> MotionComponent:
        """Create 3D hero section with Three.js."""
        return MotionComponent(
            name="3d_hero",
            framework="threejs",
            code=self._threejs_hero(),
            description=description
        )
    
    def create_animated_cards(self, description: str) -> MotionComponent:
        """Create animated card grid with GSAP."""
        return MotionComponent(
            name="animated_cards",
            framework="gsap",
            code=self._gsap_cards(),
            description=description
        )
    
    def create_react_animations(self, description: str) -> MotionComponent:
        """Create React animations with Framer Motion."""
        return MotionComponent(
            name="react_animations",
            framework="framer_motion",
            code=self._framer_animations(),
            description=description
        )
    
    def create_smooth_scroll(self, description: str) -> MotionComponent:
        """Create smooth scroll with Lenis."""
        return MotionComponent(
            name="smooth_scroll",
            framework="lenis",
            code=self._lenis_scroll(),
            description=description
        )
    
    def create_particle_background(self, description: str) -> MotionComponent:
        """Create particle background with Three.js."""
        return MotionComponent(
            name="particle_bg",
            framework="threejs",
            code=self._particle_system(),
            description=description
        )
    
    def _threejs_hero(self) -> str:
        """Three.js 3D hero section."""
        return '''<!-- Three.js 3D Hero Section -->
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<div id="hero-3d" style="height: 100vh; width: 100%;">
  <canvas id="three-canvas"></canvas>
  <div class="hero-content">
    <h1>Enterprise Dashboard</h1>
    <p>Next-generation 3D interface</p>
    <button>Get Started</button>
  </div>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('three-canvas'), alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);

// Create floating geometric shapes
const geometry = new THREE.IcosahedronGeometry(1, 0);
const material = new THREE.MeshBasicMaterial({ color: 0x6366f1, wireframe: true });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

// Ambient light
const light = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(light);

camera.position.z = 5;

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  mesh.rotation.x += 0.005;
  mesh.rotation.y += 0.005;
  renderer.render(scene, camera);
}
animate();

// Mouse interaction
document.addEventListener('mousemove', (e) => {
  mesh.position.x = (e.clientX / window.innerWidth - 0.5) * 2;
  mesh.position.y = -(e.clientY / window.innerHeight - 0.5) * 2;
});
</script>

<style>
#hero-3d {
  position: relative;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  overflow: hidden;
}

.hero-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
  z-index: 10;
}

.hero-content h1 {
  font-size: 4rem;
  margin-bottom: 1rem;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-content button {
  padding: 1rem 2rem;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.3s;
}

.hero-content button:hover {
  transform: scale(1.1);
}
</style>
'''
    
    def _gsap_cards(self) -> str:
        """GSAP animated cards."""
        return '''<!-- GSAP Animated Cards -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

<div class="cards-container">
  <div class="card card-1">
    <div class="card-icon">🚀</div>
    <h3>Fast Performance</h3>
    <p>Lightning quick load times</p>
  </div>
  <div class="card card-2">
    <div class="card-icon">🎨</div>
    <h3>Beautiful Design</h3>
    <p>Stunning user interface</p>
  </div>
  <div class="card card-3">
    <div class="card-icon">🔒</div>
    <h3>Secure</h3>
    <p>Enterprise-grade security</p>
  </div>
</div>

<script>
gsap.registerPlugin(ScrollTrigger);

// Staggered entrance animation
gsap.from('.card', {
  y: 100,
  opacity: 0,
  duration: 1,
  stagger: 0.2,
  ease: 'power3.out',
  scrollTrigger: {
    trigger: '.cards-container',
    start: 'top 80%',
  }
});

// Hover effects
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    gsap.to(card, { scale: 1.05, duration: 0.3 });
  });
  card.addEventListener('mouseleave', () => {
    gsap.to(card, { scale: 1, duration: 0.3 });
  });
});

// Parallax effect
gsap.to('.card-1', {
  y: -50,
  scrollTrigger: {
    trigger: '.cards-container',
    scrub: 1
  }
});
</script>

<style>
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s;
}

.card:hover {
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.card h3 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.card p {
  color: #64748b;
}
</style>
'''
    
    def _framer_animations(self) -> str:
        """Framer Motion React animations."""
        return '''// Framer Motion React Component
// npm install framer-motion

import { motion } from 'framer-motion';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export function AnimatedSection() {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="section"
    >
      <motion.h1 variants={item} className="title">
        Enterprise Dashboard
      </motion.h1>
      
      <motion.p variants={item} className="subtitle">
        Built for scale, designed for beauty
      </motion.p>
      
      <motion.div variants={item} className="features">
        <FeatureCard delay={0.1} icon="🚀" title="Fast" />
        <FeatureCard delay={0.2} icon="🎨" title="Beautiful" />
        <FeatureCard delay={0.3} icon="🔒" title="Secure" />
      </motion.div>
    </motion.div>
  );
}

function FeatureCard({ delay, icon, title }) {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay, type: 'spring', stiffness: 200 }}
      whileHover={{ scale: 1.1 }}
      className="feature-card"
    >
      <span className="icon">{icon}</span>
      <span className="title">{title}</span>
    </motion.div>
  );
}

// Reusable animation variants
export const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: 'easeOut' }
};

export const scaleIn = {
  initial: { scale: 0.8, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  transition: { duration: 0.4, ease: 'easeOut' }
};

export const slideIn = {
  initial: { x: -100, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  transition: { duration: 0.5, ease: 'easeOut' }
};

// Page transitions
export const pageTransition = {
  initial: { opacity: 0, x: 100 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -100 },
  transition: { duration: 0.3 }
};
'''
    
    def _lenis_scroll(self) -> str:
        """Lenis smooth scroll."""
        return '''<!-- Lenis Smooth Scroll -->
<script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.19/dist/lenis.min.js"></script>

<div class="page">
  <section class="hero">
    <h1>Smooth Scrolling</h1>
    <p>Experience buttery smooth navigation</p>
  </section>
  
  <section class="features">
    <div class="feature">Feature 1</div>
    <div class="feature">Feature 2</div>
    <div class="feature">Feature 3</div>
  </section>
</div>

<script>
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
});

function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

requestAnimationFrame(raf);

// Scroll-triggered animations
lenis.on('scroll', ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

gsap.ticker.lagSmoothing(0);
</script>

<style>
.page {
  height: 300vh;
}

section {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.hero h1 {
  font-size: 5rem;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.features {
  display: grid;
  gap: 2rem;
}

.feature {
  background: white;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}
</style>
'''
    
    def _particle_system(self) -> str:
        """Three.js particle background."""
        return '''<!-- Three.js Particle Background -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<div id="particles-bg" style="position: fixed; top: 0; left: 0; z-index: -1;"></div>

<script>
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('particles-bg').appendChild(renderer.domElement);

// Create particles
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 5000;
const posArray = new Float32Array(particlesCount * 3);

for (let i = 0; i < particlesCount * 3; i++) {
  posArray[i] = (Math.random() - 0.5) * 10;
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

const particlesMaterial = new THREE.PointsMaterial({
  size: 0.005,
  color: 0x6366f1,
  transparent: true,
  opacity: 0.8
});

const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

camera.position.z = 3;

// Mouse interaction
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX / window.innerWidth - 0.5;
  mouseY = e.clientY / window.innerHeight - 0.5;
});

// Animation
function animate() {
  requestAnimationFrame(animate);
  
  particlesMesh.rotation.y += 0.001;
  particlesMesh.rotation.x += 0.0005;
  
  // Subtle mouse follow
  particlesMesh.rotation.y += mouseX * 0.01;
  particlesMesh.rotation.x += mouseY * 0.01;
  
  renderer.render(scene, camera);
}

animate();

// Resize handler
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>

<style>
#particles-bg {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
</style>
'''


def create_motion_component(framework: str, description: str) -> MotionComponent:
    """Quick create motion component."""
    suite = MotionGraphicsSuite()
    
    if framework == 'threejs':
        return suite.create_3d_hero(description)
    elif framework == 'gsap':
        return suite.create_animated_cards(description)
    elif framework == 'framer':
        return suite.create_react_animations(description)
    elif framework == 'lenis':
        return suite.create_smooth_scroll(description)
    else:
        return suite.create_particle_background(description)
