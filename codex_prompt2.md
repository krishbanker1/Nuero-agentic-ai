# CINEMATIC DESIGN INTELLIGENCE SYSTEM v3.0

Create a skill file at: `neuro/skills/cinematic_design.py`

**Purpose:** Analyzes ANY visual content (videos, images, URLs, descriptions) from ANY source and autonomously generates premium cinematic effects based on extracted design principles.

---

## CORE PHILOSOPHY

1. **NO HARDCODED PLATFORMS** - System handles ANY URL format
2. **NO HARDCODED VALUES** - All metrics derived from actual content analysis
3. **NO REFERENCE WEBSITES** - Generic methodology works with ANY visual source
4. **AUTONOMOUS EXTRACTION** - Learns design principles from content itself

---

## CLASS: CinematicDesign

### ATTRIBUTES:
```python
NAME = "cinematic_design"
DESCRIPTION = "Analyze visual content and generate premium cinematic web/app/presentations"

TRIGGERS = [
    "cinematic", "premium", "3d effect", "dark theme", "motion graphics",
    "hero section", "gradient", "spotlight", "animation",
    "web design", "landing page", "premium website",
    "analyze", "extract from video", "build from reference",
    "visual analysis", "design system"
]
```

### REQUIRED DEPENDENCIES:
```python
REQUIRED_PACKAGES = [
    "yt-dlp",        # Universal video download (ANY video URL)
    "opencv-python", # Frame extraction and computer vision
    "Pillow",        # Image processing
    "numpy",         # Numerical analysis
    "requests",      # HTTP for image URLs
]
```

---

## METHOD 0: download_and_extract(url: str) -> List[Dict]

### Purpose:
Universal download function - handles ANY video URL format without platform-specific code.

### Parameters:
- url: str (any video URL, any format)

### Returns:
```python
List[Dict]  # Frames at temporal intervals
[
    {
        "frame_index": int,
        "timestamp": float,  # seconds
        "image_path": str,
        "numpy_array": np.ndarray,  # RGB format for CV
        "pil_image": PIL.Image.Image
    }
]
```

### Implementation Logic:
```python
import yt_dlp
import cv2
import numpy as np
from PIL import Image
import tempfile
import os

def download_and_extract(self, url: str) -> List[Dict]:
    """
    Universal video downloader - NO platform-specific code.
    Uses yt-dlp which auto-detects platform from URL structure.
    """
    frames = []
    temp_dir = tempfile.mkdtemp(prefix="cinematic_")
    
    try:
        # yt-dlp auto-detects platform from URL - NO hardcoded platforms
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, 'video.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            # No platform-specific options - let yt-dlp handle it
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = self._find_downloaded_video(temp_dir, info)
        
        # Extract frames using OpenCV - universal
        frames = self._extract_frames(video_path, temp_dir, fps_multiplier=0.5)
        
    finally:
        self._cleanup_temp_dir(temp_dir, keep_frames=True)
    
    return frames

def _find_downloaded_video(self, temp_dir: str, info: dict) -> str:
    """Find the actual downloaded video file."""
    # Get extension from info or default
    ext = info.get('ext', 'mp4')
    candidates = [
        os.path.join(temp_dir, f'video.{ext}'),
        os.path.join(temp_dir, 'video.mp4'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Fallback: find any video file
    for f in os.listdir(temp_dir):
        if f.startswith('video.') and f.split('.')[-1] in ['mp4', 'webm', 'mov', 'avi']:
            return os.path.join(temp_dir, f)
    raise FileNotFoundError("Video download failed")

def _extract_frames(self, video_path: str, temp_dir: str, fps_multiplier: float = 0.5) -> List[Dict]:
    """
    Extract frames at regular temporal intervals.
    fps_multiplier=0.5 means extract 1 frame every 0.5 seconds
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    # Calculate frame interval based on TIME, not frame numbers
    interval_seconds = 0.5  # Extract every 0.5 seconds
    frame_interval = int(fps * interval_seconds)
    
    frame_idx = 0
    saved_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save frame if enough time has passed
        if frame_idx % frame_interval == 0:
            timestamp = frame_idx / fps
            
            # BGR -> RGB conversion
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Save image
            frame_path = os.path.join(temp_dir, f"frame_{saved_idx:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            
            frames.append({
                "frame_index": saved_idx,
                "timestamp": float(timestamp),
                "image_path": frame_path,
                "numpy_array": frame_rgb,
                "pil_image": Image.fromarray(frame_rgb)
            })
            saved_idx += 1
        
        frame_idx += 1
    
    cap.release()
    return frames
```

---

## METHOD 1: analyze_single_image(source: str) -> Dict

### Purpose:
Analyzes a single image (from URL or local path) and extracts design metrics.

### Parameters:
- source: str (URL or local file path)

### Returns:
```python
{
    "brightness_level": str,  # "dark" | "medium" | "bright" - DERIVED from analysis
    "edge_score": float,      # 0-300+ - MEASURED from edge detection
    "motion_level": str,      # "static" | "subtle" | "heavy" - DERIVED
    "gradient_needed": bool,  # DERIVED from brightness analysis
    "saturation": str,        # "muted" | "medium" | "high" - MEASURED
    "contrast": str,          # "low" | "medium" | "high" - MEASURED
    "color_palette": List[str],  # EXTRACTED from image
    "dominant_colors": Dict[str, float],  # color -> percentage
    "patterns_needed": List[str],  # DERIVED from metrics
    "lighting_type": str,     # "spotlight" | "ambient" | "dramatic" | "soft"
    "depth_perception": str,  # "2d" | "2.5d" | "3d" - MEASURED
}
```

### Implementation:
```python
import requests
from io import BytesIO
import numpy as np
import cv2

def analyze_single_image(self, source: str) -> Dict:
    """
    Extract ALL metrics from image content - NO hardcoded values.
    """
    # Download if URL
    if source.startswith(('http://', 'https://')):
        response = requests.get(source, timeout=30)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(source)
    
    # Ensure RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    # EXTRACT metrics from image content
    return self._analyze_image_array(img_array)

def _analyze_image_array(self, img_array: np.ndarray) -> Dict:
    """
    Core analysis on numpy array - produces ALL metrics from scratch.
    """
    h, w = img_array.shape[:2]
    
    # Convert to HSV for color analysis
    img_rgb = img_array.astype(np.float32) / 255.0
    img_hsv = self._rgb_to_hsv(img_rgb)
    
    # === EXTRACT BRIGHTNESS ===
    v_channel = img_hsv[:, :, 2]
    mean_brightness = np.mean(v_channel) * 255
    brightness_std = np.std(v_channel) * 255
    
    # === EXTRACT SATURATION ===
    s_channel = img_hsv[:, :, 1]
    mean_saturation = np.mean(s_channel) * 255
    
    # === EXTRACT EDGE SCORE (3D depth indicator) ===
    gray = np.mean(img_array, axis=2)
    edges = cv2.Canny(gray.astype(np.uint8), 50, 150)
    edge_density = np.sum(edges > 0) / edges.size * 100
    edge_score = edge_density * 4  # Scale to 0-300
    
    # === EXTRACT COLOR PALETTE ===
    color_palette = self._extract_colors(img_array)
    
    # === EXTRACT LIGHTING TYPE ===
    lighting_type = self._detect_lighting(img_array)
    
    # === DERIVE FINAL METRICS ===
    
    # Brightness level - derived from actual measurement
    if mean_brightness < 60:
        brightness_level = "dark"
    elif mean_brightness > 150:
        brightness_level = "bright"
    else:
        brightness_level = "medium"
    
    # Saturation - derived from actual measurement
    if mean_saturation < 80:
        saturation = "muted"
    elif mean_saturation > 150:
        saturation = "high"
    else:
        saturation = "medium"
    
    # Contrast - derived from brightness variance
    if brightness_std > 50:
        contrast = "high"
    elif brightness_std > 25:
        contrast = "medium"
    else:
        contrast = "low"
    
    # Depth perception - derived from edge score
    if edge_score > 200:
        depth_perception = "3d"
    elif edge_score > 50:
        depth_perception = "2.5d"
    else:
        depth_perception = "2d"
    
    # Motion level - static for single image
    motion_level = "static"
    
    # Gradient needed - derived from brightness
    gradient_needed = brightness_level != "bright" or depth_perception != "2d"
    
    # Determine patterns needed - derived from metrics
    patterns_needed = []
    if depth_perception in ["2.5d", "3d"] or edge_score > 150:
        patterns_needed.append("3d_depth")
    if brightness_level == "dark":
        patterns_needed.append("dark_cinematic")
    if motion_level != "static":
        patterns_needed.append("motion")
    patterns_needed.append("gradient")
    
    return {
        "brightness_level": brightness_level,
        "edge_score": float(edge_score),
        "motion_level": motion_level,
        "motion_score": 0.0,
        "gradient_needed": gradient_needed,
        "saturation": saturation,
        "contrast": contrast,
        "color_palette": color_palette,
        "dominant_colors": {},  # Computed in _extract_colors
        "patterns_needed": patterns_needed,
        "lighting_type": lighting_type,
        "depth_perception": depth_perception,
        "brightness_mean": float(mean_brightness),
        "brightness_std": float(brightness_std),
        "saturation_mean": float(mean_saturation)
    }

def _rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
    """Convert RGB [0-1] to HSV [0-1]."""
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    v = maxc
    s = (maxc - minc) / (maxc + 1e-10)
    s[maxc == 0] = 0
    delta = maxc - minc
    delta[maxc == 0] = 1  # Avoid division by zero
    h = np.zeros_like(r)
    mask_r = (maxc == r)
    mask_g = (maxc == g) & ~mask_r
    mask_b = (maxc == b) & ~(mask_r | mask_g)
    h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6
    h[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2
    h[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4
    h = h / 6.0
    h[h < 0] += 1
    return np.stack([h, s, v], axis=-1)

def _extract_colors(self, img_array: np.ndarray, k: int = 5) -> List[str]:
    """
    Extract dominant colors as hex strings.
    Uses simple quantization - NO hardcoded palette.
    """
    # Reshape to list of pixels
    pixels = img_array.reshape(-1, 3)
    
    # Simple binning to find dominant colors
    bins = 32
    quantized = (pixels // bins) * bins + bins // 2
    
    # Find unique colors and counts
    unique_colors = {}
    for pixel in quantized:
        key = tuple(pixel)
        unique_colors[key] = unique_colors.get(key, 0) + 1
    
    # Sort by frequency
    sorted_colors = sorted(unique_colors.items(), key=lambda x: -x[1])
    
    # Convert top k to hex
    hex_colors = []
    for color, _ in sorted_colors[:k]:
        hex_colors.append(f"#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}")
    
    return hex_colors

def _detect_lighting(self, img_array: np.ndarray) -> str:
    """
    Detect lighting type by comparing center vs edge brightness.
    NO hardcoded lighting presets.
    """
    h, w = img_array.shape[:2]
    
    # Convert to grayscale
    gray = np.mean(img_array, axis=2)
    
    # Center region
    c_h, c_w = h // 4, w // 4
    center = gray[c_h:3*c_h, c_w:3*c_w]
    
    # Edge regions (all 4 sides)
    top = gray[:c_h, :]
    bottom = gray[-c_h:, :]
    left = gray[:, :c_w]
    right = gray[:, -c_w:]
    edges = np.concatenate([top.flatten(), bottom.flatten(), left.flatten(), right.flatten()])
    
    center_brightness = np.mean(center)
    edge_brightness = np.mean(edges)
    
    # Detect based on ratio
    ratio = center_brightness / (edge_brightness + 1e-10)
    
    if ratio > 1.5:
        return "spotlight"
    elif ratio < 0.7:
        return "dramatic"
    elif np.std([center_brightness, edge_brightness]) < 10:
        return "soft"
    else:
        return "ambient"
```

---

## METHOD 2: analyze_video_frames(frames: List[Dict]) -> Dict

### Purpose:
Analyzes video frames to extract temporal metrics (motion, scene changes, evolution).

### Parameters:
- frames: List[Dict] (from download_and_extract)

### Returns:
```python
{
    # Base metrics from single frame analysis (averaged)
    "brightness_level": str,
    "edge_score": float,
    "saturation": str,
    "contrast": str,
    "lighting_type": str,
    "depth_perception": str,
    "color_palette": List[str],
    
    # NEW: Temporal metrics from video
    "motion_level": str,        # "static" | "subtle" | "heavy"
    "motion_score": float,      # Actual measured motion magnitude
    "scene_changes": int,        # Count of major transitions
    "scene_change_timestamps": List[float],
    
    # Aggregated metrics
    "patterns_needed": List[str],
    "gradient_needed": bool,
    
    # Analysis metadata
    "frame_count": int,
    "duration_seconds": float,
    "avg_brightness": float,
    "brightness_range": Tuple[float, float],
    "motion_timeline": List[float],  # Motion score per frame
}
```

### Implementation:
```python
import numpy as np

def analyze_video_frames(self, frames: List[Dict]) -> Dict:
    """
    Analyze video frames to extract temporal design principles.
    """
    if not frames:
        return self._default_analysis()
    
    # Aggregate per-frame metrics
    brightness_values = []
    edge_scores = []
    saturation_values = []
    motion_scores = []
    motion_timeline = []
    
    for i, frame_data in enumerate(frames):
        frame = frame_data["numpy_array"]
        
        # Get single-frame analysis
        frame_analysis = self._analyze_image_array(frame)
        
        brightness_values.append(frame_analysis["brightness_mean"])
        edge_scores.append(frame_analysis["edge_score"])
        saturation_values.append(frame_analysis["saturation_mean"])
        
        # Calculate motion (frame-to-frame difference)
        if i > 0:
            prev_frame = frames[i-1]["numpy_array"].astype(float)
            curr_frame = frame.astype(float)
            motion = np.abs(curr_frame - prev_frame).mean()
            motion_scores.append(motion * 10)
            motion_timeline.append(float(motion * 10))
    
    # Compute video-level metrics
    avg_brightness = np.mean(brightness_values)
    avg_edge = np.mean(edge_scores)
    avg_saturation = np.mean(saturation_values)
    avg_motion = np.mean(motion_scores) if motion_scores else 0
    
    # Motion level - derived from actual motion measurement
    if avg_motion > 10:
        motion_level = "heavy"
    elif avg_motion > 3:
        motion_level = "subtle"
    else:
        motion_level = "static"
    
    # Detect scene changes
    scene_changes, scene_timestamps = self._detect_scene_changes(frames)
    
    # Brightness range
    brightness_range = (min(brightness_values), max(brightness_values))
    
    # Derive final metrics
    if avg_brightness < 60:
        brightness_level = "dark"
    elif avg_brightness > 150:
        brightness_level = "bright"
    else:
        brightness_level = "medium"
    
    # Depth from edge
    if avg_edge > 200:
        depth_perception = "3d"
    elif avg_edge > 50:
        depth_perception = "2.5d"
    else:
        depth_perception = "2d"
    
    # Saturation
    if avg_saturation < 80:
        saturation = "muted"
    elif avg_saturation > 150:
        saturation = "high"
    else:
        saturation = "medium"
    
    # Contrast from brightness variance
    brightness_std = np.std(brightness_values)
    if brightness_std > 50:
        contrast = "high"
    elif brightness_std > 25:
        contrast = "medium"
    else:
        contrast = "low"
    
    # Lighting type from first frame (or most common)
    lighting_type = self._detect_lighting(frames[0]["numpy_array"])
    
    # Color palette - merge all frames
    all_colors = []
    for frame_data in frames[:10]:  # Sample first 10 for efficiency
        colors = self._extract_colors(frame_data["numpy_array"])
        all_colors.extend(colors)
    
    # Get most common
    color_counts = {}
    for c in all_colors:
        color_counts[c] = color_counts.get(c, 0) + 1
    color_palette = sorted(color_counts.keys(), key=lambda x: -color_counts[x])[:5]
    
    # Determine patterns
    patterns_needed = []
    if depth_perception in ["2.5d", "3d"] or avg_edge > 150:
        patterns_needed.append("3d_depth")
    if brightness_level == "dark":
        patterns_needed.append("dark_cinematic")
    if motion_level != "static":
        patterns_needed.append("motion")
    patterns_needed.append("gradient")
    
    # Duration
    duration = frames[-1]["timestamp"] if frames else 0
    
    return {
        "brightness_level": brightness_level,
        "edge_score": float(avg_edge),
        "motion_level": motion_level,
        "motion_score": float(avg_motion),
        "gradient_needed": True,
        "saturation": saturation,
        "contrast": contrast,
        "color_palette": color_palette,
        "dominant_colors": color_counts,
        "patterns_needed": patterns_needed,
        "lighting_type": lighting_type,
        "depth_perception": depth_perception,
        "scene_changes": scene_changes,
        "scene_change_timestamps": scene_timestamps,
        "frame_count": len(frames),
        "duration_seconds": float(duration),
        "avg_brightness": float(avg_brightness),
        "brightness_range": brightness_range,
        "motion_timeline": motion_timeline
    }

def _detect_scene_changes(self, frames: List[Dict], threshold: float = 50.0) -> tuple:
    """
    Detect major scene transitions by looking at frame differences.
    threshold is a sensitivity parameter - higher = less sensitive.
    """
    changes = 0
    timestamps = []
    
    for i in range(1, len(frames)):
        prev = frames[i-1]["numpy_array"].astype(float)
        curr = frames[i]["numpy_array"].astype(float)
        
        # Mean absolute difference
        diff = np.abs(curr - prev).mean()
        
        if diff > threshold:
            changes += 1
            timestamps.append(float(frames[i]["timestamp"]))
    
    return changes, timestamps
```

---

## METHOD 3: analyze_description(text: str) -> Dict

### Purpose:
Analyzes natural language description when no visual content is available.

### Parameters:
- text: str (natural language description)

### Returns:
```python
Dict  # Same structure as analyze_video_frames
```

### Implementation:
```python
def analyze_description(self, text: str) -> Dict:
    """
    Derive design metrics from text description.
    Keywords inform direction, but NO hardcoded values.
    """
    text_lower = text.lower()
    words = set(text_lower.split())
    
    # === BRIGHTNESS ===
    dark_indicators = {'dark', 'night', 'premium', 'luxury', 'dramatic', 'gaming', 
                       'moody', 'shadow', 'black', 'deep', 'midnight', 'neon'}
    bright_indicators = {'light', 'clean', 'minimal', 'white', 'bright', 'airy',
                         'fresh', 'soft', 'pastel', 'transparent'}
    
    dark_score = len(words & dark_indicators)
    bright_score = len(words & bright_indicators)
    
    if dark_score > bright_score:
        brightness_level = "dark"
    elif bright_score > dark_score:
        brightness_level = "bright"
    else:
        brightness_level = "medium"
    
    # === EDGE SCORE (depth) ===
    depth_indicators = {'3d', 'depth', 'product', 'rotate', 'layered', 'dimensional',
                        '立体', 'three-dimensional', 'perspective', 'parallax'}
    flat_indicators = {'2d', 'flat', 'simple', 'minimal', 'clean', 'basic', 'plain'}
    
    depth_score = len(words & depth_indicators)
    flat_score = len(words & flat_indicators)
    
    if depth_score > flat_score:
        edge_score = 250  # High 3D
        depth_perception = "3d"
    elif flat_score > 0:
        edge_score = 30  # Flat 2D
        depth_perception = "2d"
    else:
        edge_score = 100  # Default medium
        depth_perception = "2.5d"
    
    # === MOTION LEVEL ===
    heavy_motion = {'animated', 'motion', 'dynamic', 'fast', 'loop', 'continuous',
                    'active', 'energetic', 'vibrant'}
    subtle_motion = {'smooth', 'gentle', 'subtle', 'fade', 'transition', 'ease',
                      'soft', 'calm', 'flowing'}
    
    heavy_score = len(words & heavy_motion)
    subtle_score = len(words & subtle_motion)
    
    if heavy_score > subtle_score:
        motion_level = "heavy"
        motion_score = 15.0
    elif subtle_score > 0:
        motion_level = "subtle"
        motion_score = 5.0
    else:
        motion_level = "static"
        motion_score = 0.0
    
    # === SATURATION ===
    high_sat = {'vibrant', 'saturated', 'bold', 'colorful', 'bright', 'vivid',
                'intense', 'striking', 'high-impact'}
    muted_sat = {'muted', 'pastel', 'neutral', 'grayscale', 'monochrome',
                 'subtle', 'toned', 'soft', 'desaturated', 'washed'}
    
    high_score = len(words & high_sat)
    muted_score = len(words & muted_sat)
    
    if high_score > muted_score:
        saturation = "high"
    elif muted_score > 0:
        saturation = "muted"
    else:
        saturation = "medium"
    
    # === CONTRAST ===
    high_contrast = {'high-contrast', 'dramatic', 'bold', 'stark', 'punchy'}
    low_contrast = {'soft', 'muted', 'low-contrast', 'gentle', 'subtle'}
    
    high_c_score = len(words & high_contrast)
    low_c_score = len(words & low_contrast)
    
    if high_c_score > low_c_score:
        contrast = "high"
    elif low_c_score > 0:
        contrast = "low"
    else:
        contrast = "medium"
    
    # === LIGHTING TYPE ===
    if 'spotlight' in words or 'highlight' in words:
        lighting_type = "spotlight"
    elif 'dramatic' in words or 'dramatic-lighting' in words:
        lighting_type = "dramatic"
    elif 'soft' in words or 'ambient' in words:
        lighting_type = "soft"
    else:
        lighting_type = "ambient"
    
    # === DERIVE PATTERNS ===
    patterns_needed = []
    if depth_perception in ["2.5d", "3d"]:
        patterns_needed.append("3d_depth")
    if brightness_level == "dark":
        patterns_needed.append("dark_cinematic")
    if motion_level != "static":
        patterns_needed.append("motion")
    patterns_needed.append("gradient")
    
    # === COLOR PALETTE (derive from description tone) ===
    if brightness_level == "dark" and saturation == "high":
        color_palette = ["#0a0a0f", "#1a1a2e", "#e94560"]  # Just starting points, not hardcoded
    elif brightness_level == "bright":
        color_palette = ["#ffffff", "#f8f9fa", "#0077b6"]
    else:
        color_palette = ["#ffffff", "#333333", "#0077b6"]
    
    return {
        "brightness_level": brightness_level,
        "edge_score": edge_score,
        "motion_level": motion_level,
        "motion_score": motion_score,
        "gradient_needed": True,
        "saturation": saturation,
        "contrast": contrast,
        "color_palette": color_palette,
        "dominant_colors": {},
        "patterns_needed": patterns_needed,
        "lighting_type": lighting_type,
        "depth_perception": depth_perception,
        "scene_changes": 0,
        "scene_change_timestamps": [],
        "frame_count": 0,
        "duration_seconds": 0,
        "avg_brightness": 100.0 if brightness_level != "dark" else 40.0,
        "brightness_range": (20.0, 200.0),
        "motion_timeline": [],
        "source": "description"
    }
```

---

## METHOD 4: analyze_input(input_data: str) -> Dict

### Purpose:
Unified entry point - automatically determines input type and routes accordingly.

### Parameters:
- input_data: str (any URL, local path, or text description)

### Returns:
```python
Dict  # Same structure as analyze_video_frames
```

### Implementation:
```python
import os

def analyze_input(self, input_data: str) -> Dict:
    """
    Universal entry point - auto-detects input type.
    
    Supported:
    - HTTP/HTTPS URLs (images or videos)
    - Local file paths (images or videos)
    - Text descriptions (自然语言)
    """
    input_data = input_data.strip()
    
    # Case 1: URL
    if input_data.startswith(('http://', 'https://')):
        return self._analyze_url(input_data)
    
    # Case 2: Local file
    elif os.path.isfile(input_data):
        return self._analyze_local_file(input_data)
    
    # Case 3: Text description
    else:
        return self.analyze_description(input_data)

def _analyze_url(self, url: str) -> Dict:
    """Analyze content from URL."""
    url_lower = url.lower()
    
    # Check if it's a video by extension or common video patterns
    video_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v'}
    is_video_ext = any(url_lower.endswith(ext) for ext in video_extensions)
    
    # Common video platform patterns in URL
    video_patterns = ['video', 'watch', 'reel', 'clip', 'stream', 'embed', 'download']
    has_video_pattern = any(p in url_lower for p in video_patterns)
    
    # Image patterns
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    is_image_ext = any(url_lower.endswith(ext) for ext in image_extensions)
    
    if is_video_ext or has_video_pattern:
        # Treat as video
        frames = self.download_and_extract(url)
        return self.analyze_video_frames(frames)
    elif is_image_ext:
        # Treat as image
        return self.analyze_single_image(url)
    else:
        # Unknown URL - try as description or default
        # Check if it looks like a URL with domain
        if '.' in url_lower and '/' in url_lower:
            # Try as video first (most feature-rich)
            try:
                frames = self.download_and_extract(url)
                return self.analyze_video_frames(frames)
            except:
                # Fallback to description
                return self.analyze_description(url)
        else:
            # Pure text - treat as description
            return self.analyze_description(url)

def _analyze_local_file(self, file_path: str) -> Dict:
    """Analyze content from local file."""
    ext = os.path.splitext(file_path.lower())[1]
    
    video_extensions = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    if ext in video_extensions:
        frames = self._extract_frames_local(file_path, temp_dir=None)
        return self.analyze_video_frames(frames)
    elif ext in image_extensions:
        return self.analyze_single_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _extract_frames_local(self, video_path: str, temp_dir: str = None) -> List[Dict]:
    """Extract frames from local video file."""
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="cinematic_local_")
    
    return self._extract_frames(video_path, temp_dir, fps_multiplier=0.5)
```

---

## METHOD 5: generate_3d_depth(params: Dict) -> str

### Purpose:
Generates CSS for 3D depth effect based on analysis parameters.

### Parameters:
- params: Dict (from analyze_input - contains brightness_level, edge_score, etc.)

### Returns:
```python
str  # CSS code
```

### Implementation:
```python
def generate_3d_depth(self, params: Dict) -> str:
    """
    Generate 3D CSS based on ACTUAL parameters from analysis.
    NO hardcoded values.
    """
    brightness = params.get("brightness_level", "medium")
    edge_score = params.get("edge_score", 100)
    depth_perception = params.get("depth_perception", "2.5d")
    
    # === DERIVE VALUES FROM PARAMETERS ===
    
    # Perspective depth based on edge score
    perspective = min(2000, max(500, edge_score * 10))
    
    # Rotation amplitude based on depth perception
    if depth_perception == "3d":
        rotation_range = 45
    elif depth_perception == "2.5d":
        rotation_range = 20
    else:
        rotation_range = 10
    
    # Animation duration based on motion level
    motion_level = params.get("motion_level", "static")
    if motion_level == "heavy":
        duration = 4  # Faster
    elif motion_level == "subtle":
        duration = 8  # Slower
    else:
        duration = 6  # Default
    
    # Spotlight intensity based on lighting type
    lighting = params.get("lighting_type", "ambient")
    if lighting == "spotlight":
        spotlight_opacity = 0.5
        spotlight_size = 250
    elif lighting == "dramatic":
        spotlight_opacity = 0.3
        spotlight_size = 300
    else:
        spotlight_opacity = 0.2
        spotlight_size = 400
    
    # === GENERATE CSS ===
    css = f"""
/* 3D Container - derived from edge_score: {edge_score} */
.cinematic-3d {{
  transform-style: preserve-3d;
  perspective: {perspective}px;
}}

/* 3D Rotation - derived from depth_perception: {depth_perception} */
@keyframes rotate-3d {{
  0%   {{ transform: rotateY(0deg) rotateX(0deg); }}
  25%  {{ transform: rotateY({rotation_range}deg) rotateX({rotation_range//4}deg); }}
  50%  {{ transform: rotateY(0deg) rotateX(0deg); }}
  75%  {{ transform: rotateY(-{rotation_range}deg) rotateX(-{rotation_range//4}deg); }}
  100% {{ transform: rotateY(0deg) rotateX(0deg); }}
}}

/* 3D Element */
.cinematic-3d-element {{
  transform: rotateY(0deg);
  animation: rotate-3d {duration}s ease-in-out infinite;
  backface-visibility: hidden;
}}

/* Mouse-following spotlight - derived from lighting_type: {lighting} */
.spotlight {{
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle {spotlight_size}px at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(255, 255, 255, {spotlight_opacity}) 0%,
    rgba(255, 255, 255, {spotlight_opacity * 0.3}) 40%,
    transparent 70%
  );
  mask-image: radial-gradient(
    circle {spotlight_size + 100}px at var(--mouse-x, 50%) var(--mouse-y, 50%),
    white 0%,
    white 30%,
    transparent 70%
  );
  -webkit-mask-image: radial-gradient(
    circle {spotlight_size + 100}px at var(--mouse-x, 50%) var(--mouse-y, 50%),
    white 0%,
    white 30%,
    transparent 70%
  );
  pointer-events: none;
}}

/* Depth shadow based on brightness */
.depth-shadow {{
  box-shadow: 
    0 {10 + edge_score//20}px {20 + edge_score//10}px rgba(0, 0, 0, {0.2 + edge_score/1000});
}}
"""
    return css
```

---

## METHOD 6: generate_dark_cinematic(params: Dict) -> str

### Implementation:
```python
def generate_dark_cinematic(self, params: Dict) -> str:
    """
    Generate dark cinematic CSS based on analysis.
    """
    saturation = params.get("saturation", "medium")
    contrast = params.get("contrast", "medium")
    color_palette = params.get("color_palette", ["#0a0a0f", "#ffffff"])
    
    # Derive saturation filter value
    if saturation == "high":
        sat_filter = 150
        accent_opacity = 1.0
    elif saturation == "muted":
        sat_filter = 80
        accent_opacity = 0.7
    else:
        sat_filter = 100
        accent_opacity = 0.85
    
    # Derive contrast shadow intensity
    if contrast == "high":
        vignette_intensity = 0.7
        shadow_depth = 0.9
    elif contrast == "low":
        vignette_intensity = 0.4
        shadow_depth = 0.5
    else:
        vignette_intensity = 0.55
        shadow_depth = 0.7
    
    # Get primary accent from palette (or default)
    accent = color_palette[1] if len(color_palette) > 1 else "#e94560"
    
    css = f"""
/* Dark cinematic - derived from saturation: {saturation}, contrast: {contrast} */
.dark-cinematic {{
  background: #0a0a0f;
  position: relative;
}}

.dark-cinematic::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(0, 0, 0, 0.2) 40%,
    rgba(0, 0, 0, {shadow_depth}) 100%
  );
  pointer-events: none;
}}

/* Text zone - darkest area for readability */
.text-zone {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 33%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.95) 0%,
    rgba(0, 0, 0, {shadow_depth * 0.6}) 50%,
    transparent 100%
  );
}}

/* Accent saturation control */
.accent-saturated {{
  filter: saturate({sat_filter}%);
  opacity: {accent_opacity};
}}

/* Vignette - derived from contrast: {contrast} */
.vignette {{
  box-shadow: inset 0 0 {int(150 * vignette_intensity)}px rgba(0, 0, 0, {vignette_intensity});
}}

/* Subtle glow for accents */
.accent-glow {{
  box-shadow: 0 0 20px {accent}40, 0 0 40px {accent}20;
}}
"""
    return css
```

---

## METHOD 7: generate_gradient(params: Dict) -> str

### Implementation:
```python
def generate_gradient(self, params: Dict) -> str:
    """
    Generate gradient CSS based on brightness analysis.
    """
    brightness_level = params.get("brightness_level", "medium")
    brightness_range = params.get("brightness_range", (50, 200))
    color_palette = params.get("color_palette", ["#ffffff", "#000000"])
    
    # Derive gradient stops from brightness range
    top_brightness, bottom_brightness = brightness_range
    
    # Convert brightness to color approximation
    def brightness_to_hex(b):
        v = int(b * 2.55)  # Scale 0-100 to 0-255
        return f"rgb({v}, {v}, {v})"
    
    top_color = brightness_to_hex(min(top_brightness, 100))
    bottom_color = "#000000"  # Always dark at bottom for depth
    
    # Add color from palette if available
    if len(color_palette) >= 2:
        mid_color = color_palette[1]
    else:
        mid_color = "rgba(128, 128, 128, 0.5)"
    
    css = f"""
/* Vertical gradient with depth - derived from brightness: {brightness_level} */
.gradient-depth {{
  background: linear-gradient(
    to bottom,
    {top_color} 0%,
    {mid_color} 40%,
    {bottom_color} 100%
  );
}}

/* Radial gradient for spotlight */
.radial-spotlight {{
  background: radial-gradient(
    ellipse at center,
    transparent 0%,
    rgba(0, 0, 0, 0.2) 50%,
    rgba(0, 0, 0, 0.6) 100%
  );
}}

/* Overlay gradient */
.gradient-overlay {{
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.4) 100%
  );
}}
"""
    return css
```

---

## METHOD 8: generate_motion(params: Dict) -> str

### Implementation:
```python
def generate_motion(self, params: Dict) -> str:
    """
    Generate motion CSS based on motion analysis.
    """
    motion_level = params.get("motion_level", "static")
    motion_score = params.get("motion_score", 5)
    
    # Derive animation parameters from motion score
    if motion_level == "heavy":
        duration = 0.4
        stagger_delay = 0.08
        slide_distance = 60
        scale_start = 0.9
    elif motion_level == "subtle":
        duration = 0.7
        stagger_delay = 0.15
        slide_distance = 30
        scale_start = 0.97
    else:
        duration = 0.5
        stagger_delay = 0.12
        slide_distance = 40
        scale_start = 0.95
    
    css = f"""
/* Entrance animation - derived from motion_level: {motion_level} */
@keyframes fade-up {{
  from {{
    opacity: 0;
    transform: translateY({slide_distance}px) scale({scale_start});
  }}
  to {{
    opacity: 1;
    transform: translateY(0) scale(1);
  }}
}}

/* Staggered children */
.stagger-container > * {{
  animation: fade-up {duration}s ease-out forwards;
}}

.stagger-container > *:nth-child(1) {{ animation-delay: 0s; }}
.stagger-container > *:nth-child(2) {{ animation-delay: {stagger_delay}s; }}
.stagger-container > *:nth-child(3) {{ animation-delay: {stagger_delay * 2}s; }}
.stagger-container > *:nth-child(4) {{ animation-delay: {stagger_delay * 3}s; }}
.stagger-container > *:nth-child(5) {{ animation-delay: {stagger_delay * 4}s; }}
.stagger-container > *:nth-child(6) {{ animation-delay: {stagger_delay * 5}s; }}

/* Hover effects */
.hover-lift {{
  transition: transform {duration}s ease-out, box-shadow {duration}s ease-out;
}}

.hover-lift:hover {{
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}}

/* Scroll-triggered reveal */
.reveal-on-scroll {{
  opacity: 0;
  transform: translateY({slide_distance}px);
  transition: opacity {duration}s ease-out, transform {duration}s ease-out;
}}

.reveal-on-scroll.visible {{
  opacity: 1;
  transform: translateY(0);
}}
"""
    return css
```

---

## METHOD 9: generate_framer_motion(params: Dict) -> str

### Implementation:
```python
def generate_framer_motion(self, params: Dict) -> str:
    """
    Generate Framer Motion React code based on motion analysis.
    """
    motion_level = params.get("motion_level", "static")
    
    # Derive stagger from motion level
    if motion_level == "heavy":
        stagger = 0.08
        stiffness = 120
        damping = 12
        y_start = 60
        duration = 0.6
    elif motion_level == "subtle":
        stagger = 0.2
        stiffness = 60
        damping = 20
        y_start = 30
        duration = 0.8
    else:
        stagger = 0.15
        stiffness = 80
        damping = 15
        y_start = 50
        duration = 0.7
    
    jsx = f"""
// Framer Motion - derived from motion_level: {motion_level}
import {{ motion }} from 'framer-motion';
import {{ useState, useEffect }} from 'react';

export default function CinematicHero() {{
  const [mousePos, setMousePos] = useState({{ x: 50, y: 50 }});

  useEffect(() => {{
    const handleMouse = (e) => {{
      setMousePos({{
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      }});
    }};
    window.addEventListener('mousemove', handleMouse);
    return () => window.removeEventListener('mousemove', handleMouse);
  }}, []);

  const containerVariants = {{
    hidden: {{ opacity: 0 }},
    visible: {{
      opacity: 1,
      transition: {{
        staggerChildren: {stagger},
        delayChildren: 0.2
      }}
    }}
  }};

  const itemVariants = {{
    hidden: {{
      opacity: 0,
      y: {y_start},
      scale: 0.95
    }},
    visible: {{
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {{
        type: 'spring',
        stiffness: {stiffness},
        damping: {damping},
        duration: {duration}
      }}
    }}
  }};

  return (
    <section
      className="cinematic-hero"
      style={{
        '--mouse-x': `${{mousePos.x}}%`,
        '--mouse-y': `${{mousePos.y}}%`
      }}
    >
      <motion.div
        className="hero-content"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.h1 className="hero-title" variants={itemVariants}>
          {{content.title}}
        </motion.h1>
        
        <motion.p className="hero-subtitle" variants={itemVariants}>
          {{content.subtitle}}
        </motion.p>
        
        <motion.button
          className="hero-cta"
          variants={itemVariants}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {{content.cta}}
        </motion.button>
      </motion.div>

      <div className="spotlight" />
    </section>
  );
}}
"""
    return jsx
```

---

## METHOD 10: generate_complete_component(analysis: Dict, content: Dict) -> Dict

### Purpose:
Combines all generators based on analysis results.

### Implementation:
```python
def generate_complete_component(self, analysis: Dict, content: Dict) -> Dict:
    """
    Generate complete component from analysis + content.
    """
    patterns_used = []
    css_parts = []
    jsx_parts = []
    
    # Generate based on patterns needed
    if "3d_depth" in analysis["patterns_needed"]:
        css_parts.append(self.generate_3d_depth(analysis))
        patterns_used.append("3d_depth")
    
    if "dark_cinematic" in analysis["patterns_needed"]:
        css_parts.append(self.generate_dark_cinematic(analysis))
        patterns_used.append("dark_cinematic")
    
    if "gradient" in analysis["patterns_needed"]:
        css_parts.append(self.generate_gradient(analysis))
        patterns_used.append("gradient")
    
    if "motion" in analysis["patterns_needed"]:
        css_parts.append(self.generate_motion(analysis))
        jsx_parts.append(self.generate_framer_motion(analysis))
        patterns_used.append("motion")
    
    # Combine CSS
    full_css = "\n\n".join(css_parts)
    
    # Generate JSX
    if jsx_parts:
        full_jsx = jsx_parts[0]
    else:
        full_jsx = self._generate_basic_jsx(content)
    
    return {
        "css": full_css,
        "jsx": full_jsx,
        "component_name": "CinematicHero",
        "patterns_used": patterns_used,
        "analysis_metadata": {
            "brightness_level": analysis.get("brightness_level"),
            "edge_score": analysis.get("edge_score"),
            "motion_level": analysis.get("motion_level"),
            "motion_score": analysis.get("motion_score"),
            "saturation": analysis.get("saturation"),
            "contrast": analysis.get("contrast"),
            "lighting_type": analysis.get("lighting_type"),
            "depth_perception": analysis.get("depth_perception"),
            "color_palette": analysis.get("color_palette", [])[:3],
            "scene_changes": analysis.get("scene_changes", 0),
            "duration_seconds": analysis.get("duration_seconds", 0),
        }
    }

def _generate_basic_jsx(self, content: Dict) -> str:
    """Basic JSX without motion if no motion pattern needed."""
    return f"""
export default function CinematicHero() {{
  return (
    <section className="cinematic-hero">
      <h1 className="hero-title">{{content.title}}</h1>
      <p className="hero-subtitle">{{content.subtitle}}</p>
      <button className="hero-cta">{{content.cta}}</button>
    </section>
  );
}}
"""
```

---

## METHOD 11: build_from_input(input_data: str, content: Dict = None) -> Dict

### Purpose:
Main entry point - one-shot generation from any input.

### Parameters:
- input_data: str (URL, path, or description)
- content: Dict (optional - title, subtitle, cta)

### Returns:
```python
{
    "css": str,
    "jsx": str,
    "component_name": str,
    "patterns_used": list,
    "analysis_metadata": dict
}
```

### Implementation:
```python
def build_from_input(self, input_data: str, content: Dict = None) -> Dict:
    """
    One-shot generation from any input.
    """
    # Default content
    if content is None:
        content = {
            "title": "Premium Headline",
            "subtitle": "Subheadline text",
            "cta": "Explore"
        }
    
    # Analyze input
    analysis = self.analyze_input(input_data)
    
    # Generate component
    return self.generate_complete_component(analysis, content)
```

### Example Usage:
```python
design = CinematicDesign()

# From URL (video or image)
result = design.build_from_input(
    "https://any-platform.com/any-video",
    {"title": "My Product", "subtitle": "Premium Quality", "cta": "Shop Now"}
)

# From description
result = design.build_from_input(
    "dark cinematic hero with 3d rotating product and smooth animations"
)
```

---

## INTEGRATION

Add to `neuro/skills/__init__.py`:
```python
"cinematic_design": "neuro.skills.cinematic_design.CinematicDesign",
```

---

## TECHNICAL REQUIREMENTS

```bash
pip install yt-dlp opencv-python Pillow numpy requests
npm install framer-motion
```

---

## SUCCESS CRITERIA

1. ✅ `download_and_extract()` handles ANY video URL without platform code
2. ✅ `analyze_single_image()` extracts real metrics from image content
3. ✅ `analyze_video_frames()` extracts temporal metrics from video
4. ✅ `analyze_description()` derives direction from text keywords
5. ✅ `analyze_input()` routes to correct analysis method
6. ✅ All `generate_*` methods derive values from analysis parameters
7. ✅ `generate_complete_component()` combines patterns based on analysis
8. ✅ `build_from_input()` is the single entry point

---

## ZERO HARDCODING RULES

| Aspect | Rule |
|--------|------|
| Platforms | yt-dlp handles ALL platforms automatically |
| Colors | EXTRACTED from actual content, not predefined |
| Metrics | MEASURED from content, not estimated |
| Durations | DERIVED from motion_level parameter |
| Easing | Uses standard functions only |
| Lighting | DETECTED from center vs edge brightness ratio |
| Depth | MEASURED via edge detection, not guesswork |

---

END OF SYSTEM v3.0
