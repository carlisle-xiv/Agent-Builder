"""
Database models for prompt exports.
"""

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
import enum

from src.database import Base


class ExportFormat(str, enum.Enum):
    """Export file formats"""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"


class PromptExport(Base):
    """
    Stores generated prompt exports in the database.
    """

    __tablename__ = "prompt_exports"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)

    # Export metadata
    agent_type = Column(String, nullable=False)
    export_format = Column(SQLEnum(ExportFormat), nullable=False)

    # Export content
    content = Column(Text, nullable=False)  # The actual export file content

    # Metadata
    file_size = Column(String, nullable=True)  # Human-readable size

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<PromptExport(id={self.id}, session_id={self.session_id}, format={self.export_format})>"
