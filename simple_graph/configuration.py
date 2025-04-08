"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional
from pydantic import Field, ConfigDict, AliasChoices, BaseModel
from pydantic import BaseModel, AliasChoices, Field, ConfigDict, model_validator
from langchain_core.runnables import RunnableConfig, ensure_config

from simple_graph import prompts
from sktaip_api.utils import AIPHeaderKeysExtraIgnore

    
class Configuration(BaseModel):
    """The configuration for the agent."""

    system_prompt: str = Field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    max_search_results: int = Field(
        default=10,
        metadata={
            "description": "The maximum number of search results to return for each search query."
        },
    )
    aip_headers: AIPHeaderKeysExtraIgnore | None = Field(default=None)
    