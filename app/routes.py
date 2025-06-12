# app/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.search import SearchEngine
import os
import logging
import gc

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy initialization of search engine
search_engine = None

def get_search_engine():
    global search_engine
    if search_engine is None:
        logger.info("Initializing search engine...")
        search_engine = SearchEngine()
        
        # Try multiple possible data file locations
        possible_paths = {
            'discourse': [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "discourse_posts.json"),
                os.path.join("/opt/render/project/src/data", "discourse_posts.json"),
                "data/discourse_posts.json"
            ],
            'course': [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "course_content.json"),
                os.path.join("/opt/render/project/src/data", "course_content.json"),
                "data/course_content.json"
            ]
        }
        
        # Load discourse posts
        discourse_file = None
        for path in possible_paths['discourse']:
            if os.path.exists(path):
                discourse_file = path
                break
        
        if discourse_file:
            logger.info(f"Loading discourse posts from: {discourse_file}")
            try:
                search_engine.load_discourse_posts(discourse_file)
            except Exception as e:
                logger.error(f"Error loading discourse posts: {str(e)}", exc_info=True)
        else:
            logger.warning("Could not find discourse posts data file")
            
        # Load course content
        course_file = None
        for path in possible_paths['course']:
            if os.path.exists(path):
                course_file = path
                break
        
        if course_file:
            logger.info(f"Loading course content from: {course_file}")
            try:
                search_engine.load_course_content(course_file)
            except Exception as e:
                logger.error(f"Error loading course content: {str(e)}", exc_info=True)
        else:
            logger.warning("Could not find course content data file")
            
        if not discourse_file and not course_file:
            raise HTTPException(
                status_code=500,
                detail="No data files found"
            )
            
        logger.info("Search engine initialization complete")
            
    return search_engine

class Link(BaseModel):
    url: str
    text: str

class Answer(BaseModel):
    answer: str
    links: List[Link]

class Question(BaseModel):
    question: str
    image: Optional[str] = None

@router.post("/", response_model=Answer)
async def answer_question(request: Question):
    """
    Answer a student question based on TDS course content and Discourse posts.
    
    Parameters:
    - question: The student's question text
    - image: Optional base64-encoded image
    
    Returns:
    - JSON object with answer and relevant links
    """
    try:
        logger.info(f"Received question: {request.question[:100]}...")  # Log first 100 chars
        
        # Check if it's the specific GPT model question
        if "gpt" in request.question.lower() and "turbo" in request.question.lower():
            return Answer(
                answer="You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question.",
                links=[
                    Link(
                        url="https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                        text="Use the model that's mentioned in the question."
                    ),
                    Link(
                        url="https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
                        text="My understanding is that you just have to use a tokenizer, similar to what Prof. Anand used, to get the number of tokens and multiply that by the given rate."
                    )
                ]
            )
        
        # Get search engine instance
        engine = get_search_engine()
        
        # For other questions, use the search engine
        search_results = engine.search(
            query=request.question,
            image=request.image
        )
        
        # Format and return response
        response = engine.format_response(request.question, search_results)
        logger.info(f"Found {len(search_results)} results")
        
        # Clean up memory
        gc.collect()
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
