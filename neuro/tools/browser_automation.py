"""Browser Automation - Browse websites, take screenshots, interact using REAL AI"""
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import base64
import io

class BrowserAutomation:
    """
    Browser automation tool for Neuro - like OpenHands browser tools.
    - Opens websites
    - Takes screenshots
    - Interacts with elements
    - Collects data
    - All using Playwright with REAL AI guidance
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    def start(self, headless: bool = True) -> Dict[str, Any]:
        """Start browser."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page(viewport={"width": 1920, "height": 1080})
        
        return {"status": "started", "headless": headless}
    
    def navigate(self, url: str, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to URL."""
        if not self.page:
            self.start()
        
        try:
            response = self.page.goto(url, timeout=timeout)
            return {
                "status": "success",
                "url": url,
                "title": self.page.title(),
                "status_code": response.status if response else None
            }
        except Exception as e:
            return {"status": "error", "url": url, "error": str(e)}
    
    def screenshot(self, path: str = "screenshot.png", full_page: bool = False) -> str:
        """Take screenshot."""
        if not self.page:
            return ""
        
        self.page.screenshot(path=path, full_page=full_page)
        return path
    
    def screenshot_base64(self, full_page: bool = False) -> str:
        """Take screenshot and return as base64."""
        if not self.page:
            return ""
        
        screenshot_bytes = self.page.screenshot(full_page=full_page)
        return base64.b64encode(screenshot_bytes).decode()
    
    def get_html(self) -> str:
        """Get current page HTML."""
        if not self.page:
            return ""
        return self.page.content()
    
    def get_text(self, selector: str = "body") -> str:
        """Get text content."""
        if not self.page:
            return ""
        try:
            return self.page.locator(selector).inner_text()
        except:
            return ""
    
    def click(self, selector: str) -> Dict[str, Any]:
        """Click element."""
        if not self.page:
            return {"status": "error", "error": "Browser not started"}
        
        try:
            self.page.locator(selector).click(timeout=5000)
            return {"status": "success", "action": "click", "selector": selector}
        except Exception as e:
            return {"status": "error", "selector": selector, "error": str(e)}
    
    def type_text(self, selector: str, text: str, delay: int = 100) -> Dict[str, Any]:
        """Type text into element."""
        if not self.page:
            return {"status": "error", "error": "Browser not started"}
        
        try:
            self.page.locator(selector).fill("")
            self.page.locator(selector).type_text(text, delay=delay)
            return {"status": "success", "action": "type", "selector": selector}
        except Exception as e:
            return {"status": "error", "selector": selector, "error": str(e)}
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element."""
        if not self.page:
            return False
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    def evaluate_js(self, script: str) -> Any:
        """Execute JavaScript."""
        if not self.page:
            return None
        return self.page.evaluate(script)
    
    def get_all_links(self) -> List[Dict[str, str]]:
        """Get all links on page."""
        if not self.page:
            return []
        
        links = []
        for a in self.page.query_selector_all("a"):
            href = a.get_attribute("href")
            text = a.inner_text()
            if href:
                links.append({"href": href, "text": text.strip()})
        return links
    
    def get_all_images(self) -> List[Dict[str, str]]:
        """Get all images on page."""
        if not self.page:
            return []
        
        images = []
        for img in self.page.query_selector_all("img"):
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            images.append({"src": src, "alt": alt or ""})
        return images
    
    def search_google(self, query: str) -> Dict[str, Any]:
        """Search Google."""
        if not self.page:
            self.start()
        
        self.page.goto(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        self.page.wait_for_load_state("networkidle")
        
        results = []
        for result in self.page.query_selector_all("div.g")[:10]:
            try:
                title = result.query_selector("h3")
                link = result.query_selector("a")
                snippet = result.query_selector("div.VwiC3b")
                
                results.append({
                    "title": title.inner_text() if title else "",
                    "link": link.get_attribute("href") if link else "",
                    "snippet": snippet.inner_text() if snippet else ""
                })
            except:
                continue
        
        return {"query": query, "results": results}
    
    def close(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.browser = None
        self.page = None
        self.playwright = None


def browse_and_analyze(url: str, headless: bool = True) -> Dict[str, Any]:
    """Browse URL and analyze content."""
    browser = BrowserAutomation()
    browser.start(headless=headless)
    
    nav_result = browser.navigate(url)
    if nav_result["status"] == "error":
        browser.close()
        return nav_result
    
    # Take screenshot
    screenshot_path = "screenshot.png"
    browser.screenshot(screenshot_path)
    
    # Get content
    html = browser.get_html()
    links = browser.get_all_links()
    images = browser.get_all_images()
    text = browser.get_text()
    title = browser.page.title() if browser.page else ""
    
    browser.close()
    
    return {
        "url": url,
        "title": title,
        "status": nav_result.get("status"),
        "screenshot": screenshot_path,
        "html": html,
        "text": text,
        "links": links,
        "images": images,
        "links_count": len(links),
        "images_count": len(images)
    }


def search_and_scrape(query: str) -> Dict[str, Any]:
    """Search Google and scrape results."""
    browser = BrowserAutomation()
    browser.start()
    
    results = browser.search_google(query)
    browser.close()
    
    return results
