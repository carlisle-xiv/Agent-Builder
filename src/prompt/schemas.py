"""
Pydantic schemas for prompt generation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class PromptFormat(str, Enum):
    """Available prompt formats for different platforms"""

    ELEVENLABS = "elevenlabs"
    OPENAI_ASSISTANT = "openai_assistant"
    OPENAI_CHAT = "openai_chat"
    ANTHROPIC = "anthropic"
    GENERIC = "generic"


class PromptExportFormat(str, Enum):
    """Export file formats"""

    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    MARKDOWN = "markdown"


class ToolConfiguration(BaseModel):
    """Tool configuration for agent"""

    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters/schema"
    )
    endpoint: Optional[str] = Field(default=None, description="API endpoint URL")
    method: str = Field(default="POST", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    extraction_rules: Dict[str, str] = Field(
        default_factory=dict,
        description="Rules for extracting data from conversation",
    )


class GeneratedPrompt(BaseModel):
    """Generated system prompt for an agent"""

    format: PromptFormat = Field(description="Prompt format/platform")
    system_prompt: str = Field(description="The generated system prompt")
    instructions: List[str] = Field(
        default_factory=list, description="Specific instructions for the agent"
    )
    examples: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Example conversations"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class PromptExport(BaseModel):
    """Complete export package for the agent"""

    session_id: str = Field(description="Source session ID")
    agent_type: str = Field(description="Type of agent")
    agent_goals: str = Field(description="Agent goals")
    agent_tone: str = Field(description="Agent tone/personality")

    prompts: Dict[str, GeneratedPrompt] = Field(
        description="Generated prompts for different formats"
    )
    tools: List[ToolConfiguration] = Field(
        default_factory=list, description="Tool configurations"
    )

    workflow_diagram: Optional[str] = Field(
        default=None, description="Mermaid workflow diagram"
    )
    workflow_summary: Optional[str] = Field(
        default=None, description="Text workflow summary"
    )

    created_at: str = Field(description="Export creation timestamp")


class PromptGenerateRequest(BaseModel):
    """Request to generate prompts for a session"""

    formats: List[PromptFormat] = Field(
        default=[PromptFormat.GENERIC],
        description="Formats to generate prompts for",
    )


class PromptExportRequest(BaseModel):
    """Request to export complete agent package"""

    export_format: PromptExportFormat = Field(
        default=PromptExportFormat.JSON,
        description="Format for the export file",
    )
    include_workflow: bool = Field(
        default=True, description="Include workflow diagram in export"
    )
    prompt_formats: List[PromptFormat] = Field(
        default=[PromptFormat.GENERIC, PromptFormat.ELEVENLABS],
        description="Prompt formats to include",
    )


__all__ = [
    "PromptFormat",
    "PromptExportFormat",
    "ToolConfiguration",
    "GeneratedPrompt",
    "PromptExport",
    "PromptGenerateRequest",
    "PromptExportRequest",
]
