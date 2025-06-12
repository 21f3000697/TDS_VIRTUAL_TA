import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from typing import List, Dict
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscourseScraper:
    def __init__(self, base_url: str = "https://discourse.onlinedegree.iitm.ac.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.output_dir = "data"
        
        # Set up headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': base_url
        })
        
    def get_topics_list(self, category_id: int, page: int = 0) -> List[Dict]:
        """Get a list of topics from a category."""
        url = f"{self.base_url}/c/{category_id}.json?page={page}"
        try:
            logger.info(f"Fetching topics from page {page}")
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            if 'topic_list' in data and 'topics' in data['topic_list']:
                return data['topic_list']['topics']
            else:
                logger.warning(f"Unexpected response format: {data.keys()}")
                return []
        except Exception as e:
            logger.error(f"Error fetching topics list: {str(e)}")
            return []

    def get_topic_posts(self, topic_id: int) -> List[Dict]:
        """Get all posts from a topic."""
        url = f"{self.base_url}/t/{topic_id}.json"
        try:
            logger.info(f"Fetching posts for topic {topic_id}")
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            if 'post_stream' in data and 'posts' in data['post_stream']:
                return data['post_stream']['posts']
            else:
                logger.warning(f"Unexpected response format: {data.keys()}")
                return []
        except Exception as e:
            logger.error(f"Error fetching topic posts: {str(e)}")
            return []

    def scrape_date_range(self, category_id: int, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape posts within a date range.
        :param category_id: Category ID to scrape
        :param start_date: Start date in YYYY-MM-DD format
        :param end_date: End date in YYYY-MM-DD format
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info(f"Starting scrape for date range {start_date} to {end_date}")
        all_posts = []
        page = 0
        
        while True:
            topics = self.get_topics_list(category_id, page)
            if not topics:
                logger.info("No more topics found")
                break
                
            for topic in topics:
                topic_date = datetime.strptime(topic['created_at'][:10], "%Y-%m-%d")
                
                if topic_date < start:
                    logger.info(f"Reached posts before {start_date}, stopping.")
                    return all_posts
                    
                if start <= topic_date <= end:
                    posts = self.get_topic_posts(topic['id'])
                    for post in posts:
                        post_date = datetime.strptime(post['created_at'][:10], "%Y-%m-%d")
                        if start <= post_date <= end:
                            all_posts.append({
                                'topic_id': topic['id'],
                                'topic_title': topic['title'],
                                'post_id': post['id'],
                                'post_number': post['post_number'],
                                'content': post['cooked'],  # HTML content
                                'created_at': post['created_at'],
                                'url': f"{self.base_url}/t/{topic['slug']}/{topic['id']}/{post['post_number']}"
                            })
                            logger.info(f"Added post {post['id']} from topic '{topic['title']}'")
                            
            page += 1
            time.sleep(2)  # Be nice to the server
            
        return all_posts

    def save_posts(self, posts: List[Dict], output_file: str = None):
        """Save scraped posts to a JSON file."""
        if output_file is None:
            output_file = os.path.join(self.output_dir, "discourse_posts.json")
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(posts)} posts to {output_file}")

if __name__ == "__main__":
    # TDS Knowledge Base category ID is 34
    scraper = DiscourseScraper()
    posts = scraper.scrape_date_range(
        category_id=34,  # TDS Knowledge Base category
        start_date="2025-01-01",
        end_date="2025-04-14"
    )
    scraper.save_posts(posts) 