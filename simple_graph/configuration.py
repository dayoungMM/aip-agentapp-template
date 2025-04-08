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
    
    # @model_validator(mode="before")
    # def from_runnable_config(
    #     cls, config: Optional[RunnableConfig] = None
    # ) -> Configuration:
    #     """Create a Configuration instance from a RunnableConfig object."""
    #     config = ensure_config(config)
    #     configurable = config.get("configurable") or {}
    #     # system_prompt = config.get("system_prompt")
    #     # max_search_results = config.get("max_search_results")
    #     # aip_headers = configurable.get("aip_headers")
    #     # return cls(**{k: v for k, v in config.items() if k in cls.__annotations__.keys()})
    #     return cls(**configurable)
