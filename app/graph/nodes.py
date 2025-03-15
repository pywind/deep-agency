import logging
from typing import Dict, Any, Annotated

from app.models.schemas import GraphState, SocialMediaType
from app.services.social_media.factory import SocialMediaAdapterFactory
from app.services.analyzer import ProfileAnalyzer


logger = logging.getLogger(__name__)


async def detect_platform(state: GraphState) -> GraphState:
    """
    Detect the social media platform from the URL.
    
    Args:
        state (GraphState): Current graph state.
        
    Returns:
        GraphState: Updated graph state with platform information.
    """
    # Try to get an adapter for the URL
    adapter = SocialMediaAdapterFactory.get_adapter_for_url(state.url)
    
    if adapter is None:
        state.error = f"Unsupported social media platform for URL: {state.url}"
        state.step = "error"
        return state
    
    # Determine platform type from adapter
    if "linkedin" in state.url.lower():
        state.platform = SocialMediaType.LINKEDIN
    # Add detection for other platforms as they are supported
    
    return state


async def fetch_profile(state: GraphState) -> GraphState:
    """
    Fetch profile data from the social media platform.
    
    Args:
        state (GraphState): Current graph state.
        
    Returns:
        GraphState: Updated graph state with profile data.
    """
    try:
        # Get the adapter for the platform
        adapter = SocialMediaAdapterFactory.get_adapter_for_platform(state.platform)
        
        if adapter is None:
            state.error = f"No adapter available for platform: {state.platform}"
            state.step = "error"
            return state
        
        # Authenticate with the platform
        authenticated = await adapter.authenticate()
        if not authenticated:
            state.error = f"Failed to authenticate with {state.platform}"
            state.step = "error"
            return state
        
        # Fetch the profile data
        state.profile_data = await adapter.get_profile(state.url)
        state.step = "fetch_posts"
        
    except Exception as e:
        logger.error(f"Error fetching profile data: {str(e)}")
        state.error = f"Error fetching profile data: {str(e)}"
        state.step = "error"
    
    return state


async def fetch_posts(state: GraphState) -> GraphState:
    """
    Fetch recent posts from the social media platform.
    
    Args:
        state (GraphState): Current graph state.
        
    Returns:
        GraphState: Updated graph state with posts data.
    """
    try:
        # Get the adapter for the platform
        adapter = SocialMediaAdapterFactory.get_adapter_for_platform(state.platform)
        
        if adapter is None:
            state.error = f"No adapter available for platform: {state.platform}"
            state.step = "error"
            return state
        
        # Fetch recent posts
        state.recent_posts = await adapter.get_recent_posts(state.url)
        state.step = "analyze"
        
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        # Continue with analysis even if posts fetch fails
        state.recent_posts = []
        state.step = "analyze"
    
    return state


async def analyze_profile(state: GraphState) -> GraphState:
    """
    Analyze the profile and posts data to extract structured information.
    
    Args:
        state (GraphState): Current graph state.
        
    Returns:
        GraphState: Updated graph state with analysis results.
    """
    try:
        if not state.profile_data:
            state.error = "No profile data available for analysis"
            state.step = "error"
            return state
        
        # Create the analyzer
        analyzer = ProfileAnalyzer()
        
        # Analyze the profile and posts
        state.analysis_result = await analyzer.analyze_profile(
            state.profile_data, 
            state.recent_posts or []
        )
        
        state.step = "complete"
        
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        state.error = f"Error analyzing profile: {str(e)}"
        state.step = "error"
    
    return state


def decide_next_step(state: GraphState) -> Annotated[str, "next_step"]:
    """
    Decide the next step in the graph based on the current state.
    
    Args:
        state (GraphState): Current graph state.
        
    Returns:
        str: Name of the next step.
    """
    return state.step 