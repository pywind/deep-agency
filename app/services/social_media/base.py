from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class SocialMediaAdapter(ABC):
    """
    Base class for all social media adapters.
    Each adapter must implement these methods to provide standardized access to platform data.
    """

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the social media platform.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        pass

    @abstractmethod
    async def get_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Fetch profile data from the given URL.
        
        Args:
            profile_url (str): URL of the profile to fetch.
            
        Returns:
            Dict[str, Any]: Profile data in a standardized format.
        """
        pass

    @abstractmethod
    async def get_recent_posts(self, profile_url: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch recent posts from the given profile.
        
        Args:
            profile_url (str): URL of the profile to fetch posts from.
            limit (int, optional): Maximum number of posts to fetch. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: List of recent posts in a standardized format.
        """
        pass

    @staticmethod
    @abstractmethod
    def can_handle_url(url: str) -> bool:
        """
        Check if this adapter can handle the given URL.
        
        Args:
            url (str): URL to check.
            
        Returns:
            bool: True if this adapter can handle the URL, False otherwise.
        """
        pass 