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

    def __repr__(self):
        return f"<Session(id={self.id}, status={self.status})>"
