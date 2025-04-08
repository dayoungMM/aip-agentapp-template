"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Literal, cast
from dotenv import load_dotenv

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai.chat_models import ChatOpenAI
from simple_graph.configuration import Configuration
from simple_graph.state import InputState, State
from simple_graph.tools import TOOLS
from sktaip_api.utils import AIPHeaderKeysExtraIgnore

async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    
    configuration = Configuration.model_validate(config.get("configurable", {}))

    # If you want to use the AIP headers, get them from the Runnable Config
    # AIP headers are used to logging in A.X Platform Gateway. If you don't want to use them, you can remove this part.
    if isinstance(configuration.aip_headers, dict):
        aip_headers: AIPHeaderKeysExtraIgnore = AIPHeaderKeysExtraIgnore.model_validate(configuration.aip_headers)
    elif isinstance(configuration.aip_headers, AIPHeaderKeysExtraIgnore):
        aip_headers = configuration.aip_headers
    else:
        raise ValueError(f"Invalid aip_headers type: {type(configuration.aip_headers)}")
    
    headers = aip_headers.get_headers_without_authorization()
    
    api_key = aip_headers.authorization
    
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=os.getenv("AIP_ENDPOINT"),
        model=os.getenv("AIP_MODEL"),
        default_headers=headers,
    )
    

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=timezone.utc).isoformat()
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages], config
        ),
    )
    
    return {"messages": [response]}


# Define a new graph
builder = StateGraph(State, input=InputState, config_schema=Configuration)

builder.add_node(call_model)


builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)


graph = builder.compile(
    interrupt_before=[],  # Add node names here to update state before they're called
    interrupt_after=[],  # Add node names here to update state after they're called
)
graph.name = "Simple Graph"  # This customizes the name in LangSmith
