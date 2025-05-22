# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT


from typing import Union, List, Optional
from langgraph.graph import MessagesState

from src.prompts.planner_model import Plan


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""
    # Runtime Variables
    locale: str = "en-US"
    observations: List[str] = []
    plan_iterations: int = 0
    # Use string type hints instead of direct imports
    current_plan: Union["Plan", str, None] = None
    final_report: str = ""
    auto_accepted_plan: bool = False
    enable_background_investigation: bool = True
    background_investigation_results: Optional[str] = None
