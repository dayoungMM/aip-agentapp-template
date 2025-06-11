"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

import os
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai.chat_models import ChatOpenAI
from simple_graph.configuration import HeaderMergedConfig, BodyConfiguration
from simple_graph.state import InputState, State


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
    
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
    )
    

    response = cast(
        AIMessage,
        await llm.ainvoke(
            [*state.messages]
        ),
    )
    
    return {"messages": [response]}


# Define a new graph
builder = StateGraph(State, input=InputState, config_schema=BodyConfiguration)

builder.add_node(call_model)


builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)


graph = builder.compile()
graph.name = "Simple Graph"  # This customizes the name in LangSmith

