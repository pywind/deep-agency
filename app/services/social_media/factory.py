from typing import List, Type, Optional

from app.services.social_media.base import SocialMediaAdapter
from app.services.social_media.linkedin import LinkedInAdapter
from app.models.schemas import SocialMediaType


class SocialMediaAdapterFactory:
    """Factory for creating social media adapters"""
    
    # Registry of all available adapters
    _adapters: List[Type[SocialMediaAdapter]] = [
        LinkedInAdapter,
        # Add new adapters here
    ]
    
    @classmethod
    def get_adapter_for_url(cls, url: str) -> Optional[SocialMediaAdapter]:
        """
        Get an appropriate adapter for the given URL.
        
        Args:
            url (str): The URL to get an adapter for.
            
        Returns:
            Optional[SocialMediaAdapter]: An instance of an adapter that can handle the URL,
                                         or None if no suitable adapter is found.
        """
        for adapter_class in cls._adapters:
            if adapter_class.can_handle_url(url):
                return adapter_class()
        return None
    
    @classmethod
    def get_adapter_for_platform(cls, platform: SocialMediaType) -> Optional[SocialMediaAdapter]:
        """
        Get an adapter for the given platform.
        
        Args:
            platform (SocialMediaType): The platform to get an adapter for.
            
        Returns:
            Optional[SocialMediaAdapter]: An instance of the appropriate adapter,
                                         or None if no suitable adapter is found.
        """
        mapping = {
            SocialMediaType.LINKEDIN: LinkedInAdapter,
            # Add new platform mappings here
        }
        
        adapter_class = mapping.get(platform)
        if adapter_class:
            return adapter_class()
        return None
    
    @classmethod
    def register_adapter(cls, adapter_class: Type[SocialMediaAdapter]) -> None:
        """
        Register a new adapter.
        
        Args:
            adapter_class (Type[SocialMediaAdapter]): The adapter class to register.
        """
        if adapter_class not in cls._adapters:
            cls._adapters.append(adapter_class) 