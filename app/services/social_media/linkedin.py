import re
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from linkedin_api import Linkedin
from bs4 import BeautifulSoup
import requests

from app.config import LINKEDIN_USERNAME, LINKEDIN_PASSWORD, MAX_POSTS_TO_ANALYZE
from app.services.social_media.base import SocialMediaAdapter


logger = logging.getLogger(__name__)


class LinkedInAdapter(SocialMediaAdapter):
    """
    Adapter for LinkedIn profiles.
    Uses the unofficial LinkedIn API client and web scraping as backup.
    """

    def __init__(self):
        self.client = None
        self.authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn"""
        if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
            logger.warning("LinkedIn credentials not set")
            return False

        try:
            self.client = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
            self.authenticated = True
            return True
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {str(e)}")
            self.authenticated = False
            return False

    def _extract_username_from_url(self, profile_url: str) -> str:
        """Extract username from LinkedIn profile URL"""
        parsed = urlparse(profile_url)
        path_parts = parsed.path.strip('/').split('/')
        if 'in' in path_parts:
            idx = path_parts.index('in')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]
        
        # Fallback to regex
        match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
        if match:
            return match.group(1)
        
        raise ValueError(f"Could not extract username from LinkedIn URL: {profile_url}")

    async def get_profile(self, profile_url: str) -> Dict[str, Any]:
        """Get LinkedIn profile data"""
        if not self.authenticated and not await self.authenticate():
            raise RuntimeError("Authentication required to access LinkedIn profiles")

        username = self._extract_username_from_url(profile_url)
        
        try:
            # Get profile data
            profile = self.client.get_profile(username)
            
            # Get additional data
            skills = self.client.get_profile_skills(username) 
            
            # Combine all data
            return {
                "profile": profile,
                "skills": skills,
                "profile_url": profile_url,
            }
        except Exception as e:
            logger.error(f"Error fetching LinkedIn profile: {str(e)}")
            raise

    async def get_recent_posts(self, profile_url: str, limit: int = MAX_POSTS_TO_ANALYZE) -> List[Dict[str, Any]]:
        """Get recent posts from LinkedIn profile"""
        if not self.authenticated and not await self.authenticate():
            raise RuntimeError("Authentication required to access LinkedIn posts")

        username = self._extract_username_from_url(profile_url)
        
        try:
            # Get recent posts
            posts = self.client.get_profile_posts(username, limit=limit)
            
            # Process and standardize post format
            processed_posts = []
            for post in posts:
                processed_post = {
                    "id": post.get("updateId", ""),
                    "text": post.get("commentary", {}).get("text", "") if post.get("commentary") else "",
                    "timestamp": post.get("timestamp", 0),
                    "likes": post.get("socialDetail", {}).get("totalSocialActivityCounts", {}).get("numLikes", 0),
                    "comments": post.get("socialDetail", {}).get("totalSocialActivityCounts", {}).get("numComments", 0),
                    "shares": post.get("socialDetail", {}).get("totalSocialActivityCounts", {}).get("numShares", 0),
                }
                processed_posts.append(processed_post)
                
            return processed_posts
        except Exception as e:
            logger.error(f"Error fetching LinkedIn posts: {str(e)}")
            # Fallback to empty list
            return []

    @staticmethod
    def can_handle_url(url: str) -> bool:
        """Check if the URL is a LinkedIn profile URL"""
        return "linkedin.com/in/" in url.lower() 