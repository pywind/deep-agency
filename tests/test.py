"""
Simple script to test the LinkedIn Profile Analyzer.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
import requests
import webbrowser

from app.graph.graph import run_profile_analyzer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_profile_analyzer():
    """Test the profile analyzer with a sample profile."""
    # Replace with a real LinkedIn profile URL
    url = "https://www.linkedin.com/in/satyanadella/"
    
    logger.info(f"Analyzing profile: {url}")
    result = await run_profile_analyzer(url)
    
    if result["error"]:
        logger.error(f"Error: {result['error']}")
    else:
        logger.info("Analysis complete!")
        # Print the profile response
        profile = result["result"]
        print(f"\nName: {profile.name}")
        print(f"Role: {profile.role}")
        print(f"Years of Experience: {profile.years_of_experience}")
        print(f"Expertise: {', '.join(profile.expertise)}")
        print(f"Skills: {', '.join(profile.skills)}")
        print(f"Tech Stack: {', '.join(profile.tech_stack)}")
        print("\nPersonality:")
        print(f"  Traits: {', '.join(profile.personality.traits)}")
        print(f"  Communication Style: {profile.personality.communication_style}")
        print(f"  Interests: {', '.join(profile.personality.interests)}")
        print(f"  Values: {', '.join(profile.personality.values)}")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY is not set in environment variables")
        print("Please create a .env file with your OpenAI API key (see .env.example)")
        exit(1)
        
    # Run the test
    asyncio.run(test_profile_analyzer())

# Your LinkedIn app credentials
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'YOUR_REDIRECT_URI'  # e.g., http://localhost:8000

# Step 1: Get authorization code
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=r_liteprofile%20r_emailaddress"
webbrowser.open(auth_url)

# Step 2: User will log in and be redirected, and you'll need to get the code from the URL
auth_code = input("Enter the authorization code from the redirect URL: ")

# Step 3: Exchange code for access token
token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
payload = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}
response = requests.post(token_url, data=payload)
access_token = response.json().get('access_token')
