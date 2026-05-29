"""Website Builder - Complete website generation using real AI"""
from typing import Dict, Any
from pathlib import Path
from neuro.router.smart_router import SmartRouter

class WebsiteBuilder:
    """Complete website builder using real AI generation."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def build(self, description: str, site_type: str = "portfolio", output_dir: str = "./output") -> Dict[str, Any]:
        """Build complete website using REAL AI."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML
        html_prompt = f"""Generate complete HTML for a {site_type} website about: {description}

Include:
- Modern responsive layout
- Navigation with smooth scrolling
- Hero section
- Features/services section
- Contact form
- Footer
- SEO meta tags
- Accessibility attributes

Use Tailwind-like inline styles for modern look.
Output ONLY HTML code, no markdown blocks.
"""
        html = self.router.chat(html_prompt, task_type="frontend_ui")
        
        # Generate CSS
        css_prompt = """Generate CSS for the HTML website with:
- Custom properties (variables)
- Responsive breakpoints
- Animations
- Hover effects
- Mobile menu styles

Output ONLY CSS, no HTML.
"""
        css = self.router.chat(css_prompt, task_type="frontend_react")
        
        # Generate JavaScript
        js_prompt = """Generate JavaScript for the website with:
- Smooth scroll navigation
- Mobile menu toggle
- Form validation
- Intersection Observer animations
- Error handling

Output ONLY JavaScript, no HTML.
"""
        js = self.router.chat(js_prompt, task_type="code_generation")
        
        # Write files to disk
        files_written = []
        index_html_path = output_path / "index.html"
        index_html_path.write_text(html)
        files_written.append(str(index_html_path))
        print(f"📄 Written: {index_html_path}")
        
        styles_css_path = output_path / "styles.css"
        styles_css_path.write_text(css)
        files_written.append(str(styles_css_path))
        print(f"📄 Written: {styles_css_path}")
        
        main_js_path = output_path / "main.js"
        main_js_path.write_text(js)
        files_written.append(str(main_js_path))
        print(f"📄 Written: {main_js_path}")
        
        print(f"\n✅ Website built in: {output_path}")
        print(f"   Output files: {files_written}")
        
        return {
            "index.html": html,
            "styles.css": css,
            "main.js": js,
            "output_dir": str(output_path),
            "files_written": files_written,
        }


def build_website(description: str, site_type: str = "portfolio", output_dir: str = "./output") -> Dict[str, Any]:
    """Quick website builder using real AI."""
    return WebsiteBuilder().build(description, site_type, output_dir)
