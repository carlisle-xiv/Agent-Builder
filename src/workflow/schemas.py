"""
Workflow schemas for structured workflow representation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class NodeType(str, Enum):
    """Types of workflow nodes"""

    START = "start"
    GREETING = "greeting"
    INTENT_DETECTION = "intent_detection"
    TOOL_CALL = "tool_call"
    RESPONSE = "response"
    CONDITION = "condition"
    END = "end"


class WorkflowNode(BaseModel):
    """A node in the workflow"""

    id: str = Field(description="Unique node identifier")
    type: NodeType = Field(description="Type of node")
    label: str = Field(description="Human-readable label")
    description: Optional[str] = Field(default=None, description="Detailed description")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Node-specific configuration"
    )
    position: Optional[Dict[str, int]] = Field(
        default=None, description="Position for visualization (x, y)"
    )


class WorkflowEdge(BaseModel):
    """An edge connecting workflow nodes"""

    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    label: Optional[str] = Field(default=None, description="Edge label (condition)")
    condition: Optional[str] = Field(
        default=None, description="Condition for this edge"
    )


class WorkflowData(BaseModel):
    """Complete workflow representation"""

    session_id: str
    agent_type: str
    goals: str
    tone: str
    use_tools: bool

    # Workflow graph
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)

    # Tool configurations
    tools: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    description: str = Field(default="", description="Workflow description")
    version: str = Field(default="1.0", description="Workflow version")


class WorkflowReviewRequest(BaseModel):
    """Request to review and optionally modify workflow"""

    session_id: str
    approved: bool = Field(description="Whether user approves the workflow")
    requested_changes: Optional[str] = Field(
        default=None, description="Changes user wants to make"
    )


class WorkflowReviewResponse(BaseModel):
    """Response after workflow review"""

    session_id: str
    workflow: WorkflowData
    mermaid_diagram: str = Field(description="Mermaid.js diagram representation")
    is_final: bool = Field(description="Whether this is the final approved workflow")


class WorkflowVisualization(BaseModel):
    """Visual representation of workflow"""

    mermaid_diagram: str = Field(description="Mermaid.js flowchart")
    json_structure: Dict[str, Any] = Field(description="JSON representation")
    summary: str = Field(description="Human-readable summary")
