# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from trustcall import create_extractor

from src.agents import create_agent
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan, StepType
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output
from src.utils.mcp_utils import extract_mcp_settings

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine
from .mcp_nodes import handle_mcp_coordination, setup_mcp_agent

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    task_title: Annotated[str, "The title of the task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


def background_investigation_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner"]]:
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke({"query": query})
        background_investigation_results = None
        if isinstance(searched_content, list):
            background_investigation_results = [
                {"title": elem["title"], "content": elem["content"]}
                for elem in searched_content
            ]
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return Command(
        update={
            "background_investigation_results": json.dumps(
                background_investigation_results, ensure_ascii=False
            )
        },
        goto="planner",
    )


def _extract_plan_with_reasoning_model(llm, messages):
    """Extract plan using reasoning model with standard LLM invocation."""
    response = llm.invoke(messages)
    
    # Extract reasoning content from response metadata
    reasoning_content = ""
    if hasattr(response, 'response_metadata') and response.response_metadata:
        reasoning_tokens = response.response_metadata.get('reasoning_tokens', 0)
        if reasoning_tokens > 0:
            reasoning_content = response.response_metadata.get('reasoning', '')
    
    # Parse the plan from the response content
    response_text = response.content
    if isinstance(response_text, list):
        response_text = str(response_text[0]) if response_text else ""
    
    plan_json = repair_json_output(response_text)
    curr_plan = json.loads(plan_json)
    extracted_plan = Plan.model_validate(curr_plan)
    
    return extracted_plan, reasoning_content


def _extract_plan_with_trustcall(llm, messages):
    """Extract plan using trustcall extractor."""
    extractor = create_extractor(llm, tools=[Plan], tool_choice="Plan")
    result = extractor.invoke({"messages": messages})
    extracted_plan = result["responses"][0]
    
    # Ensure we have a Plan object
    if not isinstance(extracted_plan, Plan):
        extracted_plan = Plan.model_validate(extracted_plan)
    
    return extracted_plan, None  # No reasoning content for non-reasoning models


def _format_plan_response(extracted_plan: Plan, reasoning_content: str = None) -> str:
    """Format the plan response with optional reasoning content."""
    plan_json = extracted_plan.model_dump_json(indent=4, exclude_none=True)
    
    if reasoning_content:
        return f"Reasoning:\n{reasoning_content}\n\nPlan:\n{plan_json}"
    else:
        return plan_json


def _create_plan_command(extracted_plan: Plan, full_response: str) -> Command[Literal["human_feedback", "reporter"]]:
    """Create the appropriate command based on plan context."""
    if extracted_plan.has_enough_context:
        logger.info("Planner response has enough context.")
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": extracted_plan,
            },
            goto="reporter",
        )
    
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner")],
            "current_plan": full_response,
        },
        goto="human_feedback",
    )


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = apply_prompt_template("planner", dict(state), configurable)

    if (
        plan_iterations == 0
        and state.get("enable_background_investigation")
        and state.get("background_investigation_results")
    ):
        background_results = state.get("background_investigation_results") or ""
        messages += [
            {
                "role": "user",
                "content": (
                    "background investigation results of user query:\n"
                    + background_results
                    + "\n"
                ),
            }
        ]

    # if the plan iterations is greater than the max plan iterations, return the reporter node
    if plan_iterations >= configurable.max_plan_iterations:
        return Command(goto="reporter")

    # Get the LLM
    llm = get_llm_by_type(AGENT_LLM_MAP["planner"])
    
    try:
        # Extract plan using appropriate method based on model type
        if AGENT_LLM_MAP["planner"] == "reasoning":
            extracted_plan, reasoning_content = _extract_plan_with_reasoning_model(llm, messages)
        else:
            extracted_plan, reasoning_content = _extract_plan_with_trustcall(llm, messages)
        
        # Format response and create command
        full_response = _format_plan_response(extracted_plan, reasoning_content)
        
        logger.debug(f"Current state messages: {state['messages']}")
        logger.info(f"Planner response: {full_response}")
        
        return _create_plan_command(extracted_plan, full_response)
        
    except Exception as e:
        logger.warning(f"Plan extraction failed: {e}")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")

        # if the feedback is not accepted, return the planner node
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # increment the plan iterations
        plan_iterations += 1
        # parse the plan
        new_plan = json.loads(current_plan)
        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )


def _handle_standard_coordination(state, configurable):
    """
    Handle coordination using standard LLM without MCP tools.
    
    Args:
        state: Current state
        configurable: Configuration object
        
    Returns:
        tuple: (goto, locale) - next node and locale
    """
    logger.info("Using standard coordinator")
    messages = apply_prompt_template("coordinator", state, configurable)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner])
        .invoke(messages)
    )
    logger.debug(f"Coordinator response: {response}")

    goto = "__end__"
    locale = state.get("locale", "en-US")
    
    if hasattr(response, "tool_calls") and len(response.tool_calls) > 0:
        goto = "planner"
        if state.get("enable_background_investigation"):
            goto = "background_investigator"
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_locale := tool_call.get("args", {}).get("locale"):
                    locale = tool_locale
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")
    
    return goto, locale


async def coordinator_node(
    state: State,
    config: RunnableConfig,
) -> Command[Literal["planner", "background_investigator", "research_team", "__end__"]]:
    """Coordinator node that communicates with customers and handles MCP tools if available."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)
    
    # Extract MCP settings for coordinator
    mcp_servers, enabled_tools = extract_mcp_settings(configurable, "coordinator")
    
    # Initialize default values
    goto = "__end__"
    locale = state.get("locale", "en-US")
    updated_messages = state["messages"]
    
    # Choose coordination approach based on available MCP servers
    if mcp_servers:
        goto, locale, updated_messages = await handle_mcp_coordination(
            state, configurable, mcp_servers, enabled_tools, [handoff_to_planner]
        )
    else:
        goto, locale = _handle_standard_coordination(state, configurable)
    
    return Command(
        update={
            "locale": locale,
            "messages": updated_messages
        },
        goto=goto,
    )


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    
    # Check if current_plan is a Plan object, not a string
    if not current_plan or isinstance(current_plan, str):
        logger.warning("No valid plan found for reporter node")
        return {"final_report": "No plan available to generate report."}
    
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_, configurable)
    observations = state.get("observations", [])

    # Add a reminder about the new report format, citation style, and table usage
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
            name="system",
        )
    )

    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    logger.debug(f"Current invoke messages: {invoke_messages}")
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    response_content = response.content
    logger.info("Reporter response completed")

    return {"final_report": response_content}


def research_team_node(
    state: State,
) -> Command[Literal["planner", "researcher", "coder"]]:
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    current_plan = state.get("current_plan")
    
    # Check if current_plan is a Plan object, not a string
    if not current_plan or isinstance(current_plan, str) or not hasattr(current_plan, 'steps'):
        return Command(goto="planner")
    
    if all(step.execution_res for step in current_plan.steps):
        return Command(goto="planner")
    for step in current_plan.steps:
        if not step.execution_res:
            break
    if step.step_type and step.step_type == StepType.RESEARCH:
        return Command(goto="researcher")
    if step.step_type and step.step_type == StepType.PROCESSING:
        return Command(goto="coder")
    return Command(goto="planner")


async def _execute_agent_step(
    state: State, agent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Check if current_plan is a Plan object, not a string
    if not current_plan or isinstance(current_plan, str) or not hasattr(current_plan, 'steps'):
        logger.warning("No valid plan found for agent execution")
        return Command(goto="research_team")

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logger.warning("No unexecuted step found")
        return Command(goto="research_team")

    logger.info(f"Executing step: {current_step.title}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i+1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    # Use the setup_mcp_agent function to configure MCP-related tools
    _, _, loaded_tools = await setup_mcp_agent(state, config, agent_type, default_tools)
    
    # Create and execute agent with configured tools
    agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
    return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        [get_web_search_tool(configurable.max_search_results), crawl_tool],
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )
