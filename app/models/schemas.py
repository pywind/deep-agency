from enum import Enum
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class SocialMediaType(str, Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    GITHUB = "github"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    X = "x"



class SocialMediaURL(BaseModel):
    """Input model for API requests"""
    url: HttpUrl = Field(..., description="URL of the social media profile")
    platform: Optional[SocialMediaType] = Field(
        None,
        description="Social media platform. If not provided, will be detected from URL"
    )


class Personality(BaseModel):
    """Personality traits extracted from the profile"""
    traits: List[str] = Field(default_factory=list, description="List of personality traits")
    communication_style: str = Field(default="", description="Communication style")
    interests: List[str] = Field(default_factory=list, description="Personal and professional interests")
    values: List[str] = Field(default_factory=list, description="Professional and personal values")


class ProfileResponse(BaseModel):
    """Response model for profile analysis"""
    name: str = Field(..., description="Full name of the person")
    role: str = Field(..., description="Current professional role")
    expertise: List[str] = Field(..., description="Areas of expertise")
    skills: List[str] = Field(..., description="Technical and soft skills")
    years_of_experience: float = Field(..., description="Total years of professional experience")
    personality: Personality = Field(..., description="Personality assessment")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies the person works with")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data extracted from social media")


class GraphState(BaseModel):
    """Internal state model for the LangGraph"""
    url: str
    platform: SocialMediaType
    profile_data: Optional[Dict[str, Any]] = None
    recent_posts: Optional[List[Dict[str, Any]]] = None
    analysis_result: Optional[ProfileResponse] = None
    error: Optional[str] = None
    step: Literal["fetch_profile", "fetch_posts", "analyze", "complete", "error"] = "fetch_profile" 