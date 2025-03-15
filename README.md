# LinkedIn Profile Analyzer

A LangGraph application that analyzes LinkedIn profiles to extract professional information, expertise, skills, experience, and personality traits.

## Features

- Retrieves profile data from LinkedIn based on profile URL
- Analyzes recent posts/activity to determine personality and interests
- Returns structured information as a dictionary
- Extensible architecture that can incorporate additional social media platforms

## Project Structure

```
.
├── README.md               # Documentation
├── requirements.txt        # Project dependencies
├── app/                    # Main application code
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Application configuration
│   ├── models/             # Pydantic models
│   │   └── schemas.py      # Data schemas
│   ├── services/           # Business logic
│   │   ├── social_media/   # Social media platform adapters
│   │   │   ├── base.py     # Base adapter interface
│   │   │   ├── linkedin.py # LinkedIn adapter
│   │   │   └── factory.py  # Factory for social media adapters
│   │   └── analyzer.py     # Profile analysis logic
│   └── graph/              # LangGraph components
│       ├── nodes.py        # Graph nodes
│       └── graph.py        # Graph definition
└── .env                    # Environment variables (not versioned)

```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with necessary API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   LINKEDIN_USERNAME=your_linkedin_username
   LINKEDIN_PASSWORD=your_linkedin_password
   ```
4. Run the application: `uvicorn app.main:app --reload`

## API Usage

The API exposes an endpoint `/analyze` that accepts a LinkedIn profile URL and returns structured information about the profile.

Example:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/in/username/"}'
```

## Extending to Other Social Media Platforms

To add a new social media platform:
1. Create a new adapter in `app/services/social_media/` that implements the base interface
2. Register the new adapter in the factory
3. No changes to the core graph logic are needed

## License

MIT 