from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ConversationStage(str, Enum):
    """Stages of the conversation flow"""

    INITIAL = "initial"  # Just started
    COLLECTING_BASICS = "collecting_basics"  # Agent type, goals, tone
    EXPLORING_TOOLS = "exploring_tools"  # Discussing tool needs
    CONFIGURING_TOOLS = "configuring_tools"  # Setting up tool details
    REVIEWING_WORKFLOW = "reviewing_workflow"  # User reviews flow
    FINALIZING = "finalizing"  # Generating final prompt
    COMPLETED = "completed"  # Done


class ToolConfigSchema(BaseModel):
    """Schema for tool configuration"""

    name: str
    description: Optional[str] = None
    endpoint: Optional[str] = None
    method: str = "POST"
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    usage_context: Optional[str] = None
    trigger_conditions: Optional[str] = None


class SessionState(BaseModel):
    """
    Complete session state stored in Redis.
    This is the working memory during an active session.
    """

    session_id: str
    stage: ConversationStage = ConversationStage.INITIAL

    # Collected information
    agent_type: Optional[str] = None
    goals: Optional[str] = None
    tone: Optional[str] = None
    use_tools: Optional[bool] = None
    tools: List[ToolConfigSchema] = Field(default_factory=list)

    # Conversation history
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)

    # Tracking what's been collected
    collected_fields: List[str] = Field(default_factory=list)

    # Workflow and final outputs
    workflow: Optional[Dict[str, Any]] = None
    final_prompt: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(BaseModel):
    """Request to create a new session"""

    initial_message: Optional[str] = None


class SessionResponse(BaseModel):
    """Response when creating or retrieving a session"""

    session_id: str
    status: SessionStatus
    stage: ConversationStage
    created_at: datetime
    message: Optional[str] = None  # AI's first question or response

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """User sending a message in a session"""

    message: str


class MessageResponse(BaseModel):
    """AI's response to user message"""

    session_id: str
    stage: ConversationStage
    ai_response: str
    is_complete: bool = False
    final_prompt: Optional[str] = None
    workflow: Optional[Dict[str, Any]] = None


class SessionStatusResponse(BaseModel):
    """Detailed session status"""

    session_id: str
    status: SessionStatus
    stage: ConversationStage
    progress_percentage: int
    collected_info: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
