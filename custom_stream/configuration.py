"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional
from pydantic import Field, ConfigDict, AliasChoices, BaseModel
from pydantic import BaseModel, AliasChoices, Field, ConfigDict, model_validator
from langchain_core.runnables import RunnableConfig, ensure_config

from simple_graph import prompts
from adxp_sdk.serves.utils import AIPHeaderKeysExtraIgnore

    
class BodyConfiguration(BaseModel):
    system_prompt: str = Field(
        default=prompts.SYSTEM_PROMPT,
        description="The system prompt to use for the agent's interactions. "
    )
    llm_provider: str | None = Field(default="oai")
class HeaderMergedConfig(BodyConfiguration):
    """The configuration for the agent."""
    aip_headers: dict| AIPHeaderKeysExtraIgnore = Field(default={})
    