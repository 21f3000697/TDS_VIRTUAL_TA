"""
Script to scrape TDS course content from tds.s-anand.net
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseContentScraper:
    """Scraper for TDS course content from tds.s-anand.net"""
    
    def __init__(self, base_url: str = "https://tds.s-anand.net/#/2025-01/"):
        self.base_url = base_url
        self.output_dir = "data"
        
    def setup_driver(self):
        """Setup Chrome driver with necessary options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use ChromeDriverManager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set window size
        driver.set_window_size(1920, 1080)
        
        return driver
        
    def scrape_content(self) -> Dict:
        """
        Scrape course content from the website
        Returns:
            Dict containing course content structure
        """
        try:
            logger.info(f"Starting content scrape from {self.base_url}")
            
            # Create new driver for this scrape
            driver = self.setup_driver()
            
            try:
                # Load the page
                driver.get(self.base_url)
                logger.info("Page loaded, waiting for content...")
                
                # Wait for initial load
                time.sleep(5)
                
                # Wait for content to load - look for the article element
                article = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                
                # Additional wait to ensure dynamic content loads
                time.sleep(2)
                
                # Get the article content
                content = article.get_attribute('innerHTML')
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract course structure
                course_data = {
                    "title": "Tools in Data Science - Jan 2025",
                    "last_updated": datetime.now().isoformat(),
                    "sections": self._extract_sections(soup),
                    "source_url": self.base_url
                }
                
                # Save the data
                self._save_content(course_data)
                return course_data
                
            finally:
                driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping course content: {str(e)}")
            raise
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract course sections and their content"""
        sections = []
        try:
            # Find all headers which typically denote sections
            headers = soup.find_all(['h1', 'h2', 'h3'])
            
            current_section = None
            current_content = []
            current_section_level = None
            
            # Process all elements
            for element in soup.children:
                # If we find a header, it's a new section
                if element.name in ['h1', 'h2', 'h3']:
                    # Save the previous section if it exists
                    if current_section:
                        sections.append({
                            "title": current_section,
                            "content": "\n".join(current_content),
                            "level": int(current_section_level[1])
                        })
                    
                    # Start a new section
                    current_section = element.get_text(strip=True)
                    current_section_level = element.name
                    current_content = []
                
                # Add content to current section
                elif current_section and element.name:
                    content_text = element.get_text(strip=True)
                    if content_text:
                        current_content.append(content_text)
            
            # Don't forget to add the last section
            if current_section:
                sections.append({
                    "title": current_section,
                    "content": "\n".join(current_content),
                    "level": int(current_section_level[1])
                })
            
            logger.info(f"Extracted {len(sections)} sections from the course content")
            
        except Exception as e:
            logger.error(f"Error extracting sections: {str(e)}")
            
        return sections
    
    def _save_content(self, data: Dict):
        """Save scraped content to JSON file"""
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, "course_content.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved course content to {output_file}")

if __name__ == "__main__":
    scraper = CourseContentScraper()
    scraper.scrape_content() 