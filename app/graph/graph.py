from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from app.models.schemas import GraphState, ProfileResponse, SocialMediaType
from app.graph.nodes import detect_platform, fetch_profile, fetch_posts, analyze_profile, decide_next_step


def create_profile_analyzer_graph():
    """
    Create the LangGraph workflow for profile analysis.
    
    Returns:
        StateGraph: The configured state graph.
    """
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("detect_platform", detect_platform)
    workflow.add_node("fetch_profile", fetch_profile)
    workflow.add_node("fetch_posts", fetch_posts)
    workflow.add_node("analyze", analyze_profile)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "detect_platform",
        decide_next_step,
        {
            "fetch_profile": "fetch_profile",
            "error": END
        }
    )
    
    workflow.add_conditional_edges(
        "fetch_profile",
        decide_next_step,
        {
            "fetch_posts": "fetch_posts",
            "error": END
        }
    )
    
    workflow.add_conditional_edges(
        "fetch_posts",
        decide_next_step,
        {
            "analyze": "analyze",
            "error": END
        }
    )
    
    workflow.add_conditional_edges(
        "analyze",
        decide_next_step,
        {
            "complete": END,
            "error": END
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("detect_platform")
    
    return workflow.compile(checkpointer=MemorySaver())


class ProfileAnalyzerGraphInput(TypedDict):
    """Input for the profile analyzer graph"""
    url: str


class ProfileAnalyzerGraphOutput(TypedDict):
    """Output of the profile analyzer graph"""
    result: Optional[ProfileResponse]
    error: Optional[str]


async def run_profile_analyzer(url: str, platform) -> ProfileAnalyzerGraphOutput:
    """
    Run the profile analyzer graph with the given URL.
    
    Args:
        url (str): URL of the social media profile to analyze.
        
    Returns:
        ProfileAnalyzerGraphOutput: Analysis results or error.
    """
    # Create the graph
    app = create_profile_analyzer_graph()

    
    # Run the graph
    config = RunnableConfig(configurable={"thread_id": 1})
    result = await app.ainvoke(input={"url": url, "platform": platform}, config=config)
    # Extract result or error
    if "analysis_result" in result:
        return {
            "result": result["analysis_result"],
            "error": None
        }
    else:
        return {
            "result": None,
            "error": result.get("error", "Unknown error occurred")
        }
