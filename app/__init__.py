"""
Initialize the application package and load environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning(".env file not found, using system environment variables")

# Check for required environment variables
REQUIRED_ENV_VARS = [
    'OPENAI_API_KEY',
]

OPTIONAL_ENV_VARS = {
    'OPENAI_MODEL': 'gpt-3.5-turbo-0125',
    'ENVIRONMENT': 'development',
    'LOG_LEVEL': 'INFO'
}

# Set optional environment variables if not already set
for var, default in OPTIONAL_ENV_VARS.items():
    if not os.getenv(var):
        os.environ[var] = default
        logger.info(f"Set {var} to default value: {default}")

# Check required environment variables
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    for var in missing_vars:
        logger.warning(f"{var} not found in environment variables")

# This file makes the app directory a Python package 