"""
API endpoints for prompt generation and export.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session as DBSession
from typing import List, Dict
import uuid

from src.database import get_db
from src.redis_client import redis_client
from src.session.models import Session, SessionStatus as DBSessionStatus
from src.session.schemas import SessionState
from src.prompt.schemas import (
    PromptFormat,
    PromptExportFormat,
    GeneratedPrompt,
    PromptExport,
    PromptGenerateRequest,
    PromptExportRequest,
)
from src.prompt.models import PromptExport as DBPromptExport, ExportFormat
from src.prompt.generator import get_prompt_generator
from src.workflow.synthesizer import get_synthesizer

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/{session_id}/generate")
async def generate_prompts(
    session_id: str,
    request: PromptGenerateRequest,
    db: DBSession = Depends(get_db),
) -> Dict[str, GeneratedPrompt]:
    """
    Generate system prompts for a session in multiple formats.

    Args:
        session_id: Session ID
        request: Generation request with formats

    Returns:
        Dictionary of generated prompts by format
    """

    # Check session exists
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get session state from Redis
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session state not found. Session may have expired.",
        )

    session_state = SessionState(**session_data)

    # Validate session has required data
    if not session_state.agent_type or not session_state.goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session must have agent_type and goals to generate prompts",
        )

    # Generate prompts
    generator = get_prompt_generator()
    prompts = generator.generate_all_prompts(session_state, request.formats)

    return prompts


@router.get("/{session_id}/export")
async def export_agent_package(
    session_id: str,
    export_format: PromptExportFormat = PromptExportFormat.JSON,
    include_workflow: bool = True,
    db: DBSession = Depends(get_db),
) -> PromptExport:
    """
    Export complete agent package including prompts, tools, and workflow.

    Args:
        session_id: Session ID
        export_format: Desired export format
        include_workflow: Whether to include workflow diagram

    Returns:
        Complete export package
    """

    # Check session exists
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get session state
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session state not found. Session may have expired.",
        )

    session_state = SessionState(**session_data)

    # Validate session has required data
    if not session_state.agent_type or not session_state.goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session must have agent_type and goals to export",
        )

    # Get workflow if requested
    workflow = None
    if include_workflow:
        synthesizer = get_synthesizer()
        workflow = synthesizer.synthesize(session_state)

    # Generate export package
    generator = get_prompt_generator()
    export_package = generator.create_export_package(
        session_state=session_state,
        workflow=workflow,
        include_workflow=include_workflow,
    )

    return export_package


@router.get("/{session_id}/export/download")
async def download_agent_package(
    session_id: str,
    format: PromptExportFormat = PromptExportFormat.JSON,
    include_workflow: bool = True,
    db: DBSession = Depends(get_db),
):
    """
    Download agent package as a file.

    First checks if export exists in database, otherwise generates it.

    Args:
        session_id: Session ID
        format: File format (json, yaml, markdown, text)
        include_workflow: Whether to include workflow

    Returns:
        File download response
    """

    # Map PromptExportFormat to ExportFormat
    format_map = {
        PromptExportFormat.JSON: ExportFormat.JSON,
        PromptExportFormat.YAML: ExportFormat.YAML,
        PromptExportFormat.MARKDOWN: ExportFormat.MARKDOWN,
        PromptExportFormat.TEXT: ExportFormat.TEXT,
    }
    db_format = format_map.get(format, ExportFormat.JSON)

    # Check if export already exists in database
    existing_export = (
        db.query(DBPromptExport)
        .filter(
            DBPromptExport.session_id == session_id,
            DBPromptExport.export_format == db_format,
        )
        .first()
    )

    if existing_export:
        # Return existing export
        content = existing_export.content
        agent_type = existing_export.agent_type
    else:
        # Generate new export
        export_package = await export_agent_package(
            session_id=session_id,
            export_format=format,
            include_workflow=include_workflow,
            db=db,
        )

        # Convert to requested format
        generator = get_prompt_generator()
        content = generator.export_to_format(export_package, format)

        # Save to database
        db_export = DBPromptExport(
            id=str(uuid.uuid4()),
            session_id=session_id,
            agent_type=export_package.agent_type,
            export_format=db_format,
            content=content,
            file_size=f"{len(content)} bytes",
        )
        db.add(db_export)
        db.commit()

        agent_type = export_package.agent_type

    # Determine content type and file extension
    content_types = {
        PromptExportFormat.JSON: ("application/json", "json"),
        PromptExportFormat.YAML: ("application/x-yaml", "yaml"),
        PromptExportFormat.MARKDOWN: ("text/markdown", "md"),
        PromptExportFormat.TEXT: ("text/plain", "txt"),
    }

    content_type, extension = content_types.get(
        format, ("application/octet-stream", "txt")
    )

    # Create filename
    filename = f"{agent_type.replace(' ', '_')}_agent.{extension}"

    # Return as downloadable file
    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{session_id}/exports")
async def list_exports(session_id: str, db: DBSession = Depends(get_db)):
    """
    List all exports for a session.

    Args:
        session_id: Session ID

    Returns:
        List of exports with metadata
    """

    # Check session exists
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get all exports for this session
    exports = (
        db.query(DBPromptExport).filter(DBPromptExport.session_id == session_id).all()
    )

    # Format response
    export_list = []
    for export in exports:
        export_list.append(
            {
                "id": export.id,
                "session_id": export.session_id,
                "agent_type": export.agent_type,
                "format": export.export_format.value,
                "file_size": export.file_size,
                "created_at": export.created_at.isoformat(),
            }
        )

    return {
        "session_id": session_id,
        "exports": export_list,
        "total": len(export_list),
    }


__all__ = ["router"]
