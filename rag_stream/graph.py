"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Literal, cast, Union
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai.chat_models import ChatOpenAI
from pydantic import SecretStr
from rag_stream.configuration import HeaderMergedConfig, BodyConfiguration
from rag_stream.state import InputState, State
from adxp_sdk.serves.utils import AIPHeaders
from typing import Callable
from langgraph.config import get_stream_writer
from rag_stream.retriever import univ_retriever, household_retriever
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import tools_condition

tools = [univ_retriever, household_retriever]


def handle_tool_error(state) -> dict:
    error = state.error
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def generator_node(
    state: State, config: RunnableConfig
) -> dict:
    
    llm = ChatOpenAI(
        api_key=os.getenv("AIP_API_KEY", "USE_YOUR_API_KEY"),
        base_url=os.getenv("AIP_MODEL_ENDPOINT", "http://aip.sktai.io/api/v1/gateway"),
        model=os.getenv("AIP_MODEL")
    )

    chain = llm.bind_tools(tools)
    result = chain.invoke(state.messages)

    return {"messages": result}


def output_parser_node(
    state: State, config: RunnableConfig
) -> dict:
    if isinstance(state.messages[-2], ToolMessage):
        tool_result = state.messages[-2].content
    else:
        tool_result = None

            
    try:
        # retriever tool의 결과는 str(list[dict]) 이므로, 파싱 가능한 경우에만 파싱
        if isinstance(tool_result, str):
            tool_result = json.loads(tool_result)
    except Exception:
        pass
    if isinstance(state.messages[-1], AIMessage):
        final_result = state.messages[-1].content
    else:
        final_result = "[Error] Failed to generate response"
    return {"messages": [], "content" : final_result, "docs": tool_result}



def choose_next(
    state: State,
    messages_key: str = "messages",
) -> Literal["tools", "output_parser"]:
    """tool 계획(tool_calls)잇으면 tools로, ai messages만 있으면 output_parser로"""
    ai_message = state.messages[-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "output_parser"



# Define a new graph        
builder = StateGraph(State, input=InputState)


builder.add_node("generator", generator_node)
builder.add_node("tools", ToolNode(tools))
builder.add_node("output_parser", output_parser_node)


builder.add_edge(START, "generator")
builder.add_conditional_edges("generator", choose_next)
builder.add_edge("tools", "generator")
builder.add_edge("output_parser", END)


graph = builder.compile()
graph.name = "RAG Graph" 


"""curl example
### stream
curl -X 'POST' \
  'http://127.0.0.1:18080/stream' \
  -H 'accept: application/json' \
  -H 'aip-user: ai_agent_eng' \
  -H 'secret-mode: false' \
  -H 'Authorization: 1234' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": {
    "messages": [{"content": "올해 수시 특징은?", "type": "human" }]
  },
  "config": {},
  "kwargs": {}
}'

### invoke
curl -X 'POST' \
  'http://127.0.0.1:18080/invoke' \
  -H 'accept: application/json' \
  -H 'aip-user: ai_agent_eng' \
  -H 'secret-mode: false' \
  -H 'Authorization: 1234' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": {
    "messages": [{"content": "올해 수시 특징은?", "type": "human" }]
  },
  "config": {},
  "kwarg

"""