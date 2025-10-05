"""
Database models for workflow storage.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class Workflow(Base):
    """
    Persistent workflow storage.
    Stores the compiled workflow for each session.
    """

    __tablename__ = "workflows"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, nullable=False)

    # Agent configuration
    agent_type = Column(String, nullable=False)
    goals = Column(Text, nullable=False)
    tone = Column(String, nullable=False)
    use_tools = Column(Boolean, default=False, nullable=False)

    # Workflow data (JSON)
    workflow_json = Column(Text, nullable=False)  # Full WorkflowData as JSON
    mermaid_diagram = Column(Text, nullable=True)  # Mermaid visualization

    # Status
    is_approved = Column(Boolean, default=False, nullable=False)
    version = Column(String, default="1.0", nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Workflow(id={self.id}, session_id={self.session_id}, agent_type={self.agent_type})>"
