from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from src.database import Base
import enum


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Session(Base):
    """
    Persistent session record in database.
    Stores metadata about each session, while active state is in Redis.
    """

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    status = Column(
        SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Store final outputs when session completes
    final_prompt = Column(Text, nullable=True)
    workflow_json = Column(Text, nullable=True)
    tools_config = Column(Text, nullable=True)

    # Store detailed agent specifications
    agent_type = Column(String, nullable=True)
    goals = Column(Text, nullable=True)
    tone = Column(String, nullable=True)
    target_users = Column(Text, nullable=True)
    greeting_style = Column(Text, nullable=True)
    conversation_flow = Column(Text, nullable=True)
    example_interactions = Column(Text, nullable=True)  # JSON array as text
    constraints = Column(Text, nullable=True)  # JSON array as text
    edge_cases = Column(Text, nullable=True)  # JSON array as text
    escalation_rules = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    brand_voice = Column(Text, nullable=True)
    verbosity_level = Column(String, nullable=True)
    additional_notes = Column(Text, nullable=True)
    use_tools = Column(String, nullable=True)  # "true", "false", or null

    def __repr__(self):
        return f"<Session(id={self.id}, status={self.status}, agent_type={self.agent_type})>"
