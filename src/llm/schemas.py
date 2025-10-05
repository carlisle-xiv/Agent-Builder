from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ExtractedData(BaseModel):
    """Structured data extracted from user messages"""

    agent_type: Optional[str] = None
    goals: Optional[str] = None
    tone: Optional[str] = None
    use_tools: Optional[bool] = None
    tool_details: Optional[Dict[str, Any]] = None

    # Detailed specifications
    target_users: Optional[str] = None
    greeting_style: Optional[str] = None
    conversation_flow: Optional[str] = None
    example_interactions: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    edge_cases: Optional[List[str]] = None
    escalation_rules: Optional[str] = None
    success_criteria: Optional[str] = None
    brand_voice: Optional[str] = None
    verbosity_level: Optional[str] = None
    additional_notes: Optional[str] = None


class ConfidenceScores(BaseModel):
    """Confidence scores for extracted data"""

    agent_type: float = 0.0
    goals: float = 0.0
    tone: float = 0.0
    use_tools: float = 0.0
    tool_details: float = 0.0


class LLMResponse(BaseModel):
    """Structured response from LLM"""

    next_question: str = Field(description="The next question to ask the user")
    extracted_data: ExtractedData = Field(
        description="Data extracted from user's message"
    )
    confidence: ConfidenceScores = Field(
        default_factory=ConfidenceScores,
        description="Confidence scores for extracted data",
    )
    needs_clarification: bool = Field(
        default=False, description="Whether clarification is needed"
    )
    clarification_question: Optional[str] = Field(
        default=None, description="Specific clarification question if needed"
    )
    stage_complete: bool = Field(
        default=False, description="Whether current stage is complete"
    )
    reasoning: str = Field(default="", description="Internal reasoning (for debugging)")


class LLMRequest(BaseModel):
    """Request to LLM"""

    system_prompt: str
    user_message: str
    conversation_history: list
    context: Dict[str, Any]
