"""
Script to scrape both course content and Discourse posts for TDS Virtual TA
"""
import logging
from app.scraper import DiscourseScraper
from app.course_scraper import CourseContentScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run both scrapers to collect all required data"""
    try:
        # 1. Scrape course content
        logger.info("Starting course content scraping...")
        course_scraper = CourseContentScraper()
        course_data = course_scraper.scrape_content()
        logger.info("Course content scraping completed")
        
        # 2. Scrape Discourse posts
        logger.info("Starting Discourse posts scraping...")
        discourse_scraper = DiscourseScraper()
        posts = discourse_scraper.scrape_date_range(
            category_id=34,  # TDS Knowledge Base category
            start_date="2025-01-01",
            end_date="2025-04-14"
        )
        discourse_scraper.save_posts(posts)
        logger.info("Discourse posts scraping completed")
        
        logger.info("All data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data collection: {str(e)}")
        raise

if __name__ == "__main__":
    main() 