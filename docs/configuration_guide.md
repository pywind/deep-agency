# Configuration Guide

## Quick Settings

Copy the `conf.yaml.example` file to `conf.yaml` and modify the configurations to match your specific settings and requirements.

```bash
cp conf.yaml.example conf.yaml
```

## Which models does DeerFlow support?

In DeerFlow, currently we only support non-reasoning models, which means models like OpenAI's o1/o3 or DeepSeek's R1 are not supported yet, but we will add support for them in the future.

### Supported Models

`doubao-1.5-pro-32k-250115`, `gpt-4o`, `qwen-max-latest`, `gemini-2.0-flash`, `deepseek-v3`, and theoretically any other non-reasoning chat models that implement the OpenAI API specification.

> [!NOTE]
> The Deep Research process requires the model to have a **longer context window**, which is not supported by all models.
> A work-around is to set the `Max steps of a research plan` to `2` in the settings dialog located on the top right corner of the web page,
> or set `max_step_num` to `2` when invoking the API.

### How to switch models?
You can switch the model in use by modifying the `conf.yaml` file in the root directory of the project, using the configuration in the [litellm format](https://docs.litellm.ai/docs/providers/openai_compatible).

---

### How to use OpenAI-Compatible models?

DeerFlow supports integration with OpenAI-Compatible models, which are models that implement the OpenAI API specification. This includes various open-source and commercial models that provide API endpoints compatible with the OpenAI format. You can refer to [litellm OpenAI-Compatible](https://docs.litellm.ai/docs/providers/openai_compatible) for detailed documentation.
The following is a configuration example of `conf.yaml` for using OpenAI-Compatible models:

```yaml
# An example of standard OpenAI models
BASIC_MODEL:
  model: "gpt-4o"
  api_key: YOUR_OPENAI_API_KEY
  # Optionally use an environment variable:
  api_key: $OPENAI_API_KEY

# An example of Doubao models served by VolcEngine
BASIC_MODEL:
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  model: "doubao-1.5-pro-32k-250115"
  api_key: YOUR_API_KEY

# An example of Aliyun models
BASIC_MODEL:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-max-latest"
  api_key: YOUR_API_KEY

# An example of deepseek official models
BASIC_MODEL:
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"
  api_key: YOU_API_KEY

# An example of Google Gemini models using OpenAI-Compatible interface
BASIC_MODEL:
  base_url: "https://generativelanguage.googleapis.com/v1beta/openai/"
  model: "gemini-2.0-flash"
  api_key: YOUR_API_KEY
```

### How to use Ollama models?

DeerFlow supports the integration of Ollama models. You can refer to [litellm Ollama](https://docs.litellm.ai/docs/providers/ollama). <br>
The following is a configuration example of `conf.yaml` for using Ollama models:

```yaml
BASIC_MODEL:
  model: "ollama/ollama-model-name"
  base_url: "http://localhost:11434" # Local service address of Ollama, which can be started/viewed via ollama serve
```

### How to use OpenRouter models?

DeerFlow supports the integration of OpenRouter models. You can refer to [litellm OpenRouter](https://docs.litellm.ai/docs/providers/openrouter). To use OpenRouter models, you need to:
1. Obtain the OPENROUTER_API_KEY from OpenRouter (https://openrouter.ai/) and set it in the environment variable.
2. Add the `openrouter/` prefix before the model name.
3. Configure the correct OpenRouter base URL.

The following is a configuration example for using OpenRouter models:
1. Configure OPENROUTER_API_KEY in the environment variable (such as the `.env` file)
```ini
OPENROUTER_API_KEY=""
```
2. Set the model name in `conf.yaml`
```yaml
BASIC_MODEL:
  model: "openrouter/google/palm-2-chat-bison"
```

Note: The available models and their exact names may change over time. Please verify the currently available models and their correct identifiers in [OpenRouter's official documentation](https://openrouter.ai/docs).

### How to use Azure models?

DeerFlow supports the integration of Azure models. You can refer to [litellm Azure](https://docs.litellm.ai/docs/providers/azure). Configuration example of `conf.yaml`:
```yaml
BASIC_MODEL:
  model: "azure/gpt-4o-2024-08-06"
  api_base: $AZURE_API_BASE
  api_version: $AZURE_API_VERSION
  api_key: $AZURE_API_KEY
```

## MCP Integration Guide

DeerFlow supports the Model Control Protocol (MCP) for integrating external tools into the UI. There are two transport types supported: `stdio` and `sse`.

### Setting up an MCP Server

#### Option 1: Standard IO (stdio)

This option runs a command as a subprocess and communicates with it using standard input/output.

```yaml
# Example for adding a stdio MCP server in the settings UI
{
  "transport": "stdio",
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "API_KEY": "your-api-key-here"
  }
}
```

Example for a Python-based MCP server implementation:

```python
# simple_mcp_server.py
from mcp import ServerSession
from mcp.server.stdio import stdio_server

# Define a tool
def my_tool(param1: str, param2: int) -> str:
    """
    A simple example tool.
    
    Args:
        param1: A string parameter
        param2: An integer parameter
        
    Returns:
        A result string
    """
    return f"Processed {param1} with value {param2}"

# Register your tools
tools = [my_tool]

# Run the server
if __name__ == "__main__":
    with stdio_server() as (read, write):
        with ServerSession(read, write, tools=tools) as session:
            session.run()
```

#### Option 2: Server-Sent Events (SSE)

This option connects to an SSE endpoint on a web server.

```yaml
# Example for adding an SSE MCP server in the settings UI
{
  "transport": "sse",
  "url": "http://localhost:3000/sse",
  "env": {
    "API_KEY": "your-api-key-here"
  }
}
```

### Adding MCP Servers in the UI

DeerFlow provides a simple interface for adding MCP servers through the Settings page.

1. Go to Settings in the DeerFlow UI
2. Navigate to the "MCP Servers" tab
3. Click "Add Server" 
4. You'll see the "Add New Server" dialog with the following fields:

   ![Add MCP Server Dialog](./images/add_mcp_server.png)

   - **Server Name**: Enter a descriptive name for your server (e.g., api-service, data-processor)
   - **Connection Type**: Choose between:
     - **Standard IO**: For subprocess-based communication
     - **SSE**: For Server-Sent Events communication
   
   For Standard IO connections:
   - **Command**: Enter the command to execute (e.g., `python`)
   - **Arguments**: Enter the command arguments (e.g., `-m mcp_server`)
   
   For SSE connections:
   - **URL**: Enter the SSE endpoint URL

5. Click "Add Server" to save and connect to your MCP server

Example configuration for a Standard IO server:
- Server Name: `tavily-search`
- Connection Type: Standard IO
- Command: `npx`
- Arguments: `-y tavily-mcp@0.1.3`

Example configuration for an SSE server:
- Server Name: `web-tools`
- Connection Type: SSE
- URL: `http://localhost:3000/api/mcp/sse`

### Using MCP Tools in Chat

When you start a new chat, you can enable MCP tools for specific agents:

```json
{
  "mcp_settings": {
    "servers": {
      "my-server-name": {
        "transport": "stdio", 
        "command": "python",
        "args": ["-m", "my_mcp_server"],
        "env": {
          "API_KEY": "your-api-key-here"
        },
        "enabled_tools": ["my_tool_name"],
        "add_to_agents": ["researcher"]
      }
    }
  }
}
```

### MCP Server Implementation Resources

- Official MCP documentation: [MCP GitHub Repository](https://github.com/llmOS/mcp)
- Available transports: stdio, sse
- Required Python packages: `mcp` 
- Implementation examples are available in the DeerFlow source code under `src/tools/`
