"""Define a custom Reasoning and Action agent using RunnableGenerator.

Works with a chat model with tool calling support.
"""

import os
import json
import httpx
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Literal, Any, AsyncIterator, Iterator
from dotenv import load_dotenv

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig, RunnableGenerator
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai.chat_models import ChatOpenAI
from pydantic import SecretStr
from custom_stream.configuration import HeaderMergedConfig, BodyConfiguration
from custom_stream.state import InputState, State
from custom_stream.tools import TOOLS
from adxp_sdk.serves.utils import AIPHeaderKeysExtraIgnore
from typing import Callable
from langgraph.config import get_stream_writer

async def stream_model(
    input: AsyncIterator[Any]
) -> AsyncIterator[str]:
    """Stream the LLM response using RunnableGenerator.

    Args:
        input (AsyncIterator[Any]): The input stream from RunnableGenerator.

    Yields:
        str: Tokenized response from the model.
    """
    load_dotenv()
    url = os.getenv("PAAS_STG_ENDPOINT")
    if not url:
        raise ValueError("URL is not set in environment variables")

    headers = {
        "Content-Type": "application/json",
        "Client-Name": "adot-biz"
    }

    # Get the first item from the input stream
    input_data = None
    async for item in input:
        input_data = item
        break

    if not input_data or not isinstance(input_data, dict):
        error_msg = "Invalid input: Expected dictionary with messages"
        yield error_msg
        return

    # Extract messages from input
    messages = []
    input_messages = input_data.get("messages", [])
    for msg in input_messages:
        if isinstance(msg, dict):
            message = {
                "role": msg.get("role", ""),
                "content": msg.get("content", "")
            }
            messages.append(message)
    
    if not messages:
        error_msg = "No valid messages found in input"
        yield error_msg
        return

    payload = {
        "messages": messages,
        "model_extensions": {
            "return_citations": True,
            "support_multi_turn": True,
            "use_internal_contents": False,
            "news_filter_off": True
        }
    }
    print(f"[PAYLOAD] {payload}")
  
    timeout = int(os.getenv("TIMEOUT", "30"))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if not line or line.strip() == "":
                        continue
                    print(f"[RAW LINE] {line}")
                    if not line.startswith("data:"):
                        error_msg = f"Invalid line format (missing 'data:'): {line}"
                        yield error_msg
                        continue
                    try:
                        parsed_line = line[len("data:"):].strip()
                        if parsed_line == "[DONE]":
                            yield parsed_line
                            continue
                        data_obj = json.loads(parsed_line)
                        yield data_obj
                    except Exception as e:
                        error_msg = f"Error processing line: {str(e)}"
                        yield error_msg
    except Exception as e:
        tb = traceback.format_exc()
        error_msg = f"[ERROR] {str(e) if str(e) else repr(e)}\n{tb}"
        yield error_msg

# Create RunnableGenerator
runnable = RunnableGenerator(stream_model)