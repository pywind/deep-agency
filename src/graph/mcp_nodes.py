
import logging
import os
from typing import Dict, Any, List, Tuple

from langchain_core.messages import trim_messages
from langchain_core.messages.utils import count_tokens_approximately
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableConfig
from src.agents import create_agent
from src.config.configuration import Configuration
from src.graph.types import State
from src.prompts.template import apply_prompt_template
from src.utils.mcp_utils import extract_mcp_settings

logger = logging.getLogger(__name__)


async def process_tool_calls(messages: List[Any], state: State) -> Tuple[str, str]:
    """
    Process tool calls from messages to determine next workflow step and locale.
    
    Args:
        messages: Messages potentially containing tool calls
        state: Current state
        
    Returns:
        tuple: (goto, locale) - next node and locale
    """
    goto = "__end__"
    locale = state.get("locale", "en-US")
    
    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.get("name", "") == "handoff_to_planner":
                    goto = "planner"
                    if state.get("enable_background_investigation"):
                        goto = "background_investigator"
                    if tool_locale := tool_call.get("args", {}).get("locale"):
                        locale = tool_locale
                    break
            if goto != "__end__":
                break
    
    return goto, locale


async def handle_mcp_coordination(
    state: State, 
    configurable: Configuration,
    mcp_servers: Dict[str, Dict[str, Any]],
    enabled_tools: Dict[str, str],
    default_tools: List[Any]
) -> Tuple[str, str, List[Any]]:
    """
    Handle coordination using MCP tools.
    
    Args:
        state: Current state
        configurable: Configuration object
        mcp_servers: Dictionary of MCP server configurations
        enabled_tools: Dictionary mapping tool names to server names
        default_tools: List of default tools to include
        
    Returns:
        tuple: (goto, locale, updated_messages) - next node, locale, and updated messages
    """
    logger.info("Using MCP coordinator with available tools")
    default_recursion_limit = 25
    env_value_str = int(os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit)))
    
    # Create and execute agent with MCP tools
    async with MultiServerMCPClient(mcp_servers) as client:
        # Prepare tools
        loaded_tools = default_tools.copy() if default_tools else []
        
        # Add MCP tools
        for tool in client.get_tools():
            if tool.name in enabled_tools:
                tool.description = (
                    f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                )
                loaded_tools.append(tool)
        logger.info(f"Loaded tools: {loaded_tools}")
        # Create agent with tools
        agent = create_agent(
            "mcp_coordinator", "mcp_coordinator", loaded_tools, "mcp_coordinator"
        )
        
        agent_input = {
            "messages": apply_prompt_template("mcp_coordinator", state, configurable)
        }

        # Invoke agent
        agent_response = await agent.ainvoke(
            input=agent_input, config={"recursion_limit": env_value_str}
        )
        
        # Update messages with agent response
        updated_messages = state["messages"] + agent_response.get("messages", [])
        
        # Process tool calls
        goto, locale = await process_tool_calls(
            agent_response.get("messages", []), state
        )
        
    return goto, locale, updated_messages


async def setup_mcp_agent(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: List[Any]
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str], List[Any]]:
    """
    Set up an MCP agent with appropriate tools.
    
    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent
        default_tools: The default tools to add to the agent
        
    Returns:
        Tuple containing:
        - mcp_servers: Dictionary of server configurations
        - enabled_tools: Dictionary mapping tool names to their server names
        - loaded_tools: List of tools loaded for the agent
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers, enabled_tools = extract_mcp_settings(configurable, agent_type)
    
    loaded_tools = default_tools.copy() if default_tools else []
    
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
    
    return mcp_servers, enabled_tools, loaded_tools 