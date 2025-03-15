import logging
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from app.config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from app.models.schemas import ProfileResponse, Personality


logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """
    Service for analyzing profile data and extracting structured information.
    Uses LangChain and OpenAI to analyze the profile.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE
        )
        
    async def analyze_profile(
        self, 
        profile_data: Dict[str, Any], 
        posts_data: List[Dict[str, Any]]
    ) -> ProfileResponse:
        """
        Analyze profile data and posts to extract structured information.
        
        Args:
            profile_data (Dict[str, Any]): Profile data from social media adapter
            posts_data (List[Dict[str, Any]]): Recent posts data from social media adapter
            
        Returns:
            ProfileResponse: Structured profile information
        """
        # Prepare the data for analysis
        profile_str = self._format_profile_data(profile_data)
        posts_str = self._format_posts_data(posts_data)
        
        # Create the analysis prompt
        prompt = ChatPromptTemplate.from_template(
            """
            You are a professional personality and career analyst specializing in analyzing 
            professional profiles. I'll provide you with data from a LinkedIn profile and 
            recent posts. Analyze this information to extract structured details.
            
            ### PROFILE DATA:
            {profile_data}
            
            ### RECENT POSTS/ACTIVITY:
            {posts_data}
            
            Based on this information, provide a detailed analysis in the following JSON format:
            ```json
            {
                "name": "Full name of the person",
                "role": "Current professional role or title",
                "expertise": ["List of areas of expertise, e.g. 'Machine Learning'"],
                "skills": ["List of technical and soft skills"],
                "years_of_experience": "Estimated total years of professional experience as a number",
                "tech_stack": ["Technologies the person works with"],
                "personality": {
                    "traits": ["List of personality traits"],
                    "communication_style": "Description of communication style",
                    "interests": ["Personal and professional interests"],
                    "values": ["Professional and personal values"]
                }
            }
            ```
            
            Analyze both the explicit details from the profile and the implicit information from 
            the writing style and content of posts. Make educated estimations where data is missing.
            
            Provide ONLY the valid JSON in your response, with no additional text.
            """
        )
        
        # Create the chain
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            # Run the chain
            result = await chain.ainvoke({
                "profile_data": profile_str,
                "posts_data": posts_str
            })
            
            # Convert to ProfileResponse model
            profile_response = ProfileResponse(
                name=result.get("name", ""),
                role=result.get("role", ""),
                expertise=result.get("expertise", []),
                skills=result.get("skills", []),
                years_of_experience=float(result.get("years_of_experience", 0)),
                tech_stack=result.get("tech_stack", []),
                personality=Personality(**result.get("personality", {
                    "traits": [],
                    "communication_style": "",
                    "interests": [],
                    "values": []
                })),
                raw_data={"profile": profile_data, "posts": posts_data}
            )
            
            return profile_response
        except Exception as e:
            logger.error(f"Error analyzing profile: {str(e)}")
            raise
    
    def _format_profile_data(self, profile_data: Dict[str, Any]) -> str:
        """
        Format profile data as a string for analysis.
        
        Args:
            profile_data (Dict[str, Any]): Profile data
            
        Returns:
            str: Formatted profile data string
        """
        profile = profile_data.get("profile", {})
        skills = profile_data.get("skills", [])
        
        # Format the profile data
        sections = []
        
        # Basic info
        sections.append("BASIC INFORMATION:")
        if profile.get("firstName") and profile.get("lastName"):
            sections.append(f"Name: {profile.get('firstName')} {profile.get('lastName')}")
        if profile.get("headline"):
            sections.append(f"Headline: {profile.get('headline')}")
        if profile.get("summary"):
            sections.append(f"Summary: {profile.get('summary')}")
        if profile.get("industryName"):
            sections.append(f"Industry: {profile.get('industryName')}")
        if profile.get("locationName"):
            sections.append(f"Location: {profile.get('locationName')}")
        
        # Experience
        if profile.get("experience"):
            sections.append("\nEXPERIENCE:")
            for exp in profile.get("experience", []):
                company = exp.get("companyName", "")
                title = exp.get("title", "")
                date_range = f"{exp.get('timePeriod', {}).get('startDate', {}).get('year', '')} - {exp.get('timePeriod', {}).get('endDate', {}).get('year', 'Present')}"
                description = exp.get("description", "")
                sections.append(f"- {title} at {company} ({date_range})")
                if description:
                    sections.append(f"  Description: {description}")
        
        # Education
        if profile.get("education"):
            sections.append("\nEDUCATION:")
            for edu in profile.get("education", []):
                school = edu.get("schoolName", "")
                degree = edu.get("degreeName", "")
                field = edu.get("fieldOfStudy", "")
                date_range = f"{edu.get('timePeriod', {}).get('startDate', {}).get('year', '')} - {edu.get('timePeriod', {}).get('endDate', {}).get('year', 'Present')}"
                sections.append(f"- {degree} {field} at {school} ({date_range})")
        
        # Skills
        if skills:
            sections.append("\nSKILLS:")
            for skill in skills:
                sections.append(f"- {skill.get('name', '')}")
        
        return "\n".join(sections)
    
    def _format_posts_data(self, posts_data: List[Dict[str, Any]]) -> str:
        """
        Format posts data as a string for analysis.
        
        Args:
            posts_data (List[Dict[str, Any]]): Posts data
            
        Returns:
            str: Formatted posts data string
        """
        if not posts_data:
            return "No recent posts available."
        
        sections = []
        
        for i, post in enumerate(posts_data, 1):
            sections.append(f"POST {i}:")
            sections.append(f"Content: {post.get('text', 'No content')}")
            sections.append(f"Engagement: {post.get('likes', 0)} likes, {post.get('comments', 0)} comments, {post.get('shares', 0)} shares")
            sections.append("")
        
        return "\n".join(sections) 