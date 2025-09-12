"""Define the state structures for the agent."""

from __future__ import annotations


from typing import Annotated, Any, Dict, Optional, Sequence, List
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated
from langgraph.graph.message import AnyMessage, add_messages
from adxp_sdk.knowledges.schemas import RetrievalResult
def add_or_clear(
    left_messages: list[AnyMessage], right_messages: list[AnyMessage] | None
) -> list[AnyMessage]:
    """
    - Args:
        - left_messages: list[AnyMessage]
        - right_messages: list[AnyMessage] | None
            - None: no update
            - [] : clear messages
            - [AnyMessage] : add messages
    - Returns:
        - list[AnyMessage]
    """
    if right_messages is None:
        return left_messages
    elif isinstance(right_messages, list) and len(right_messages) == 0:
        return []
    return add_messages(left_messages, right_messages)  # type: ignore

class InputState(BaseModel):
    """사용자에게 받을 Input 정의"""

    messages: Annotated[list[AnyMessage], add_or_clear] = []
    
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """


class State(InputState):
    """그래프 내에서 사용하고 response되는 State
    """
    content: str = Field(default="")
    docs: Any | None = Field(default=None)
