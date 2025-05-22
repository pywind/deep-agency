
from typing import Dict, Tuple, Any

from src.config.configuration import Configuration


def extract_mcp_settings(
    configurable: Configuration, agent_type: str
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    """
    Extract MCP server configuration for a specific agent type.
    
    Args:
        configurable: Configuration object containing MCP settings
        agent_type: Type of agent to extract settings for (e.g., "researcher", "coder")
        
    Returns:
        Tuple containing:
        - mcp_servers: Dictionary of server configurations
        - enabled_tools: Dictionary mapping tool names to their server names
    """
    mcp_servers = {}
    enabled_tools = {}
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name
    
    return mcp_servers, enabled_tools 