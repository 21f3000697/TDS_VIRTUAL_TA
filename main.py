#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from app.routes import router as api_router
import logging
import sys
import uvicorn
from dotenv import load_dotenv
load_dotenv()
import os
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Log environment setup
logger.info("Starting application setup...")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")

model_name = os.getenv("MODEL_NAME", "paraphrase-MiniLM-L3-v2")
logger.info(f"Using model: {model_name}")

# Set environment variables to limit memory usage
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:64'  # Limit CUDA memory splits
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizer parallelism
os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'  # More aggressive memory trimming

app = FastAPI(
    title="TDS Virtual TA",
    version="1.0",
    docs_url="/docs",  # Explicitly set the docs URL
    redoc_url="/redoc",  # Explicitly set the redoc URL
    openapi_url="/openapi.json"  # Explicitly set the OpenAPI schema URL
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that provides basic information about the API"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>TDS Virtual TA API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>TDS Virtual TA API</h1>
            <p>Welcome to the TDS Virtual TA API. This API provides answers to questions about the TDS course.</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/docs">/docs</a> - Interactive API documentation</li>
                <li><a href="/redoc">/redoc</a> - Alternative API documentation</li>
                <li><code>/api/</code> - Main API endpoint for questions (POST requests only)</li>
                <li><a href="/health">/health</a> - Health check endpoint</li>
            </ul>
            <h2>Example Usage:</h2>
            <pre>
POST /api/
Content-Type: application/json

{
    "question": "How do I calculate tokens?"
}
            </pre>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if we have the necessary environment variables
        env_status = {
            "OPENAI_API_KEY": "present" if os.getenv("OPENAI_API_KEY") else "missing",
            "MODEL_NAME": os.getenv("MODEL_NAME", "default"),
        }
        
        return JSONResponse({
            "status": "healthy",
            "environment": env_status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Include API routes
app.include_router(api_router, prefix="/api")

logger.info("Application setup completed successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT env var
    uvicorn.run("main:app", host="0.0.0.0", port=port)