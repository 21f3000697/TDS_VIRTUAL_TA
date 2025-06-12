# TDS Virtual TA 🤖

A virtual Teaching Assistant (TA) that answers student questions from the IITM Tools in Data Science (TDS) course using semantic search and natural language processing.

## Project Overview 📋

This project creates a virtual TA that can automatically answer student questions based on:
- Course content from TDS Jan 2025 batch (scraped from https://tds.s-anand.net/#/2025-01/)
- TDS Discourse posts from Jan 1, 2025 to Apr 14, 2025 (scraped from https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34)

## Features 🌟

- Automated data collection from course website and Discourse forum
- Semantic search over TDS course content and Discourse posts
- Handles both text questions and image attachments
- Provides relevant answers with source links
- Easy-to-use REST API endpoint
- Automatic text extraction from images (OCR)

## Project Structure 📁

```
TDS_Virtual_TA/
├── app/
│   ├── __init__.py
│   ├── course_scraper.py    # Course content scraper
│   ├── scraper.py          # Discourse posts scraper
│   └── routes.py           # API routes
├── data/
│   ├── course_content.json # Scraped course content
│   └── discourse_posts.json # Scraped Discourse posts
├── main.py                 # FastAPI application
├── scrape_data.py         # Data collection script
└── requirements.txt       # Project dependencies
```

## Setup Instructions 🛠️

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tds-virtual-ta.git
   cd tds-virtual-ta
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Collect Data**
   ```bash
   python scrape_data.py
   ```
   This will:
   - Scrape course content from tds.s-anand.net
   - Scrape Discourse posts from the specified date range
   - Save data in the `data` directory

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

## Data Collection Details 📊

### Course Content Scraping
- Source: https://tds.s-anand.net/#/2025-01/
- Uses Selenium for JavaScript rendering
- Extracts structured content with sections and subsections
- Saves to `data/course_content.json`

### Discourse Posts Scraping
- Source: https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34
- Date Range: Jan 1, 2025 - Apr 14, 2025
- Extracts posts with metadata and content
- Saves to `data/discourse_posts.json`

## API Usage 📚

### POST /api/
Accept a question and optional image, returns an answer with relevant links.

**Request Body:**
```json
{
  "question": "Your question here",
  "image": "Optional base64-encoded image"
}
```

**Response:**
```json
{
  "answer": "Answer based on course content",
  "links": [
    {
      "url": "URL to relevant discussion",
      "text": "Title of discussion"
    }
  ]
}
```

## API Documentation 📖

- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Environment Variables ⚙️

Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=paraphrase-MiniLM-L3-v2
```

## Deployment 🚀

### Deploy to Render

1. Fork this repository to your GitHub account

2. Create a new Web Service on Render:
   - Go to https://dashboard.render.com
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Choose a name for your service
   - Select "Python 3" as the environment
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables from `.env`
   - Click "Create Web Service"

3. Your app will be deployed to a URL like: `https://your-app-name.onrender.com`

## Requirements 📋

Key dependencies:
- Python 3.8+
- FastAPI
- Selenium (for course content scraping)
- BeautifulSoup4 (for parsing HTML)
- Requests (for API calls)
- Other dependencies listed in `requirements.txt`

## Contributing 🤝

Feel free to open issues or submit pull requests for improvements.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.
