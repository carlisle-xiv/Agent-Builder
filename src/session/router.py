from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from typing import Optional
import uuid
import json
from datetime import datetime

from src.database import get_db
from src.redis_client import redis_client
from src.session.models import Session, SessionStatus as DBSessionStatus
from src.session.schemas import (
    SessionCreate,
    SessionResponse,
    SessionState,
    MessageRequest,
    MessageResponse,
    SessionStatusResponse,
    ConversationStage,
)
from src.orchestrator import get_orchestrator
from src.workflow.models import Workflow
from src.workflow.synthesizer import get_synthesizer
from src.workflow.visualizer import generate_mermaid_diagram

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_initial_question() -> str:
    """Get the first question to ask the user"""
    return (
        "Hello! I'm here to help you design a voice agent. "
        "To get started, what kind of voice agent would you like to create? "
        "For example, are you building a customer support agent, a booking assistant, "
        "an educational tutor, or something else?"
    )


@router.post(
    "/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_session(request: SessionCreate, db: DBSession = Depends(get_db)):
    """
    Create a new session for agent building.
    Returns session_id and first question.
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Create session in database
    db_session = Session(id=session_id, status=DBSessionStatus.ACTIVE)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Initialize session state in Redis
    session_state = SessionState(session_id=session_id, stage=ConversationStage.INITIAL)

    # If user provided initial message, add it to history
    if request.initial_message:
        session_state.conversation_history.append(
            {
                "role": "user",
                "content": request.initial_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    # Store in Redis
    redis_client.set_session(session_id, session_state.model_dump(mode="json"))

    return SessionResponse(
        session_id=session_id,
        status=DBSessionStatus.ACTIVE,
        stage=ConversationStage.INITIAL,
        created_at=db_session.created_at,
        message=get_initial_question(),
    )


@router.post("/{session_id}/message", response_model=MessageResponse)
async def send_message(
    session_id: str, request: MessageRequest, db: DBSession = Depends(get_db)
):
    """
    Send a user message to the session.
    The orchestrator will process it and respond.
    """
    # Check if session exists in DB
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if db_session.status != DBSessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session {session_id} is not active (status: {db_session.status})",
        )

    # Get session state from Redis
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session state not found in cache. Session may have expired.",
        )

    session_state = SessionState(**session_data)

    # Add user message to history
    session_state.conversation_history.append(
        {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Process message through orchestrator
    orchestrator = get_orchestrator()
    result = await orchestrator.process_message(session_state, request.message)

    # Extract results
    ai_response = result["ai_response"]
    updated_state = result["updated_state"]
    is_complete = result["is_complete"]
    stage_changed = result["stage_changed"]
    new_stage = result.get("new_stage")

    # Add AI response to history
    updated_state.conversation_history.append(
        {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Auto-create workflow in database when entering REVIEWING_WORKFLOW stage
    if stage_changed and new_stage == ConversationStage.REVIEWING_WORKFLOW:
        # Check if workflow already exists
        existing_workflow = (
            db.query(Workflow).filter(Workflow.session_id == session_id).first()
        )

        if not existing_workflow:
            print(f"💾 Auto-creating workflow in database for session {session_id}")

            # Synthesize workflow from session state
            synthesizer = get_synthesizer()
            workflow_data = synthesizer.synthesize(updated_state)

            # Generate visualization
            mermaid_diagram = generate_mermaid_diagram(workflow_data)

            # Create workflow record in PostgreSQL
            db_workflow = Workflow(
                id=str(uuid.uuid4()),
                session_id=session_id,
                agent_type=workflow_data.agent_type,
                goals=workflow_data.goals,
                tone=workflow_data.tone,
                use_tools=workflow_data.use_tools,
                workflow_json=workflow_data.model_dump_json(),
                mermaid_diagram=mermaid_diagram,
                is_approved=False,
            )
            db.add(db_workflow)
            print(
                f"✅ Workflow created with {len(workflow_data.nodes)} nodes and {len(workflow_data.edges)} edges"
            )

    # Update Redis with new state
    redis_client.set_session(session_id, updated_state.model_dump(mode="json"))

    # Update DB timestamp and status
    db_session.updated_at = datetime.utcnow()

    # Save detailed agent specifications to PostgreSQL
    db_session.agent_type = updated_state.agent_type
    db_session.goals = updated_state.goals
    db_session.tone = updated_state.tone
    db_session.target_users = updated_state.target_users
    db_session.greeting_style = updated_state.greeting_style
    db_session.conversation_flow = updated_state.conversation_flow
    db_session.escalation_rules = updated_state.escalation_rules
    db_session.success_criteria = updated_state.success_criteria
    db_session.brand_voice = updated_state.brand_voice
    db_session.verbosity_level = updated_state.verbosity_level
    db_session.additional_notes = updated_state.additional_notes
    db_session.use_tools = (
        str(updated_state.use_tools) if updated_state.use_tools is not None else None
    )

    # Store arrays as JSON strings
    if updated_state.example_interactions:
        db_session.example_interactions = json.dumps(updated_state.example_interactions)
    if updated_state.constraints:
        db_session.constraints = json.dumps(updated_state.constraints)
    if updated_state.edge_cases:
        db_session.edge_cases = json.dumps(updated_state.edge_cases)

    if is_complete:
        db_session.status = DBSessionStatus.COMPLETED
        db_session.completed_at = datetime.utcnow()

    db.commit()

    return MessageResponse(
        session_id=session_id,
        stage=updated_state.stage,
        ai_response=ai_response,
        is_complete=is_complete,
    )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str, db: DBSession = Depends(get_db)):
    """
    Get current status of a session.
    """
    # Check DB
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Get from Redis
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session state not found. Session may have expired.",
        )

    session_state = SessionState(**session_data)

    # Calculate progress
    total_fields = 3  # agent_type, goals, tone (minimum)
    collected = len(session_state.collected_fields)
    if session_state.use_tools:
        total_fields += len(session_state.tools)
    progress = min(int((collected / total_fields) * 100), 100)

    # Collected info summary
    collected_info = {
        "agent_type": session_state.agent_type,
        "goals": session_state.goals,
        "tone": session_state.tone,
        "use_tools": session_state.use_tools,
        "tools_count": len(session_state.tools),
    }

    return SessionStatusResponse(
        session_id=session_id,
        status=db_session.status,
        stage=session_state.stage,
        progress_percentage=progress,
        collected_info=collected_info,
        created_at=db_session.created_at,
        updated_at=session_state.updated_at,
    )


@router.post("/{session_id}/resume", response_model=MessageResponse)
async def resume_session(session_id: str, db: DBSession = Depends(get_db)):
    """
    Resume a paused session.
    Returns the context and next question.
    """
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session state expired. Cannot resume.",
        )

    session_state = SessionState(**session_data)

    # Extend session expiry
    redis_client.extend_session(session_id)

    # Generate a resume message
    resume_message = (
        f"Welcome back! We were working on creating your {session_state.agent_type or 'voice agent'}. "
        f"Let's continue where we left off."
    )

    return MessageResponse(
        session_id=session_id,
        stage=session_state.stage,
        ai_response=resume_message,
        is_complete=False,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: DBSession = Depends(get_db)):
    """
    Delete a session (mark as abandoned).
    """
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Update DB status
    db_session.status = DBSessionStatus.ABANDONED
    db.commit()

    # Delete from Redis
    redis_client.delete_session(session_id)

    return {"message": f"Session {session_id} deleted successfully"}
