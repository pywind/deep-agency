import logging
from typing import

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.models.schemas import SocialMediaURL, ProfileResponse
from app.graph.graph import run_profile_analyzer
from app.config import HOST, PORT


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LinkedIn Profile Analyzer",
    description="API for analyzing LinkedIn profiles using LangGraph",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LinkedIn Profile Analyzer API",
        "docs_url": "/docs",
        "endpoints": {
            "analyze": "/analyze"
        }
    }


@app.post("/analyze", response_model=ProfileResponse)
async def analyze_profile(social_media: SocialMediaURL):
    """
    Analyze a social media profile and extract structured information.
    
    Args:
        social_media (SocialMediaURL): Social media profile URL to analyze.
        
    Returns:
        ProfileResponse: Structured profile information.
        
    Raises:
        HTTPException: If the analysis fails.
    """
    try:
        # Run the profile analyzer
        url = str(social_media.url)
        platform = social_media.platform
        result = await run_profile_analyzer(url, platform)
        
        if result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result["result"]
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing profile: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True) 