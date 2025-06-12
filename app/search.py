# search.py
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from typing import List, Dict
import torch
from PIL import Image
import easyocr
import base64
import io
import json
import gc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2"):  # Smaller model
        # Force CPU usage to save memory
        self.device = "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self.discourse_posts = []
        self.course_content = []
        self.discourse_embeddings = None
        self.course_embeddings = None
        self.reader = None  # Initialize OCR only when needed
        
    def load_discourse_posts(self, json_file: str):
        """Load discourse posts from JSON file and compute embeddings."""
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.discourse_posts = json.load(f)
                logger.info(f"Loaded {len(self.discourse_posts)} posts from {json_file}")
                
                # Compute embeddings for posts
                texts = [post['content'] for post in self.discourse_posts]
                self.discourse_embeddings = self.model.encode(texts, convert_to_tensor=True)
                logger.info(f"Computed embeddings for {len(texts)} discourse posts")
                
        except Exception as e:
            logger.error(f"Error loading discourse posts: {str(e)}")
            raise
            
    def load_course_content(self, json_file: str):
        """Load course content from JSON file and compute embeddings."""
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.course_content = json.load(f)['sections']
                logger.info(f"Loaded {len(self.course_content)} sections from {json_file}")
                
                # Compute embeddings for course content
                texts = [f"{section['title']}\n{section['content']}" for section in self.course_content]
                self.course_embeddings = self.model.encode(texts, convert_to_tensor=True)
                logger.info(f"Computed embeddings for {len(texts)} course sections")
                
        except Exception as e:
            logger.error(f"Error loading course content: {str(e)}")
            raise
            
    def extract_text_from_image(self, base64_image: str) -> str:
        """Extract text from base64 encoded image using OCR."""
        try:
            if self.reader is None:
                self.reader = easyocr.Reader(['en'])
                
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            results = self.reader.readtext(np.array(image))
            
            # Extract text
            text = ' '.join([result[1] for result in results])
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
            
    def search(self, query: str, image: str = None, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant content using semantic similarity.
        Returns top_k most relevant results combining both course content and discourse posts.
        """
        try:
            if (self.discourse_embeddings is None and self.course_embeddings is None) or \
               (len(self.discourse_posts) == 0 and len(self.course_content) == 0):
                logger.warning("No content available. Make sure content is loaded.")
                return []
                
            # Combine query with any text from image
            if image:
                image_text = self.extract_text_from_image(image)
                query = f"{query} {image_text}"
                
            logger.info(f"Processing query: {query}")
                
            # Get query embedding
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            query_embedding = query_embedding.to(self.device)
            
            results = []
            
            # Search course content
            if self.course_embeddings is not None and len(self.course_content) > 0:
                similarities = torch.nn.functional.cosine_similarity(
                    query_embedding.unsqueeze(0),
                    self.course_embeddings,
                    dim=1
                )
                
                scores, indices = torch.topk(similarities, min(top_k, len(self.course_content)))
                
                for score, idx in zip(scores.tolist(), indices.tolist()):
                    if score > 0.3:  # Minimum similarity threshold
                        section = self.course_content[idx]
                        results.append({
                            'source': 'course',
                            'content': section['content'],
                            'title': section['title'],
                            'similarity': score,
                            'url': 'https://tds.s-anand.net/#/2025-01/'
                        })
            
            # Search discourse posts
            if self.discourse_embeddings is not None and len(self.discourse_posts) > 0:
                similarities = torch.nn.functional.cosine_similarity(
                    query_embedding.unsqueeze(0),
                    self.discourse_embeddings,
                    dim=1
                )
                
                scores, indices = torch.topk(similarities, min(top_k, len(self.discourse_posts)))
                
                for score, idx in zip(scores.tolist(), indices.tolist()):
                    if score > 0.3:  # Minimum similarity threshold
                        post = self.discourse_posts[idx]
                        results.append({
                            'source': 'discourse',
                            'content': post['content'],
                            'title': post['topic_title'],
                            'similarity': score,
                            'url': post['url']
                        })
            
            # Sort all results by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Take top_k results
            results = results[:top_k]
            
            logger.info(f"Found {len(results)} relevant results")
            
            # Clear memory
            del query_embedding
            torch.cuda.empty_cache()
            gc.collect()
                    
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []

    def format_response(self, query: str, search_results: List[Dict]) -> Dict:
        """Format the response with answer and relevant links."""
        if not search_results:
            return {
                "answer": "I apologize, but I couldn't find any relevant information to answer your question. Please try rephrasing your question or contact the course staff directly.",
                "links": []
            }
            
        # Format the answer based on the most relevant result
        best_match = search_results[0]
        
        # Format links from all relevant results
        links = []
        for result in search_results:
            links.append({
                "url": result['url'],
                "text": f"[{result['source']}] {result['title']}"
            })
            
        # Format answer based on source
        if best_match['source'] == 'course':
            answer = f"According to the course content:\n\n{best_match['content']}"
        else:
            answer = f"From the Discourse forum:\n\n{best_match['content']}"
            
        return {
            "answer": answer,
            "links": links
        }
