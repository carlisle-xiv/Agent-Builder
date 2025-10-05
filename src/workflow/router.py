"""
Workflow API endpoints for viewing, reviewing, and modifying workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
import uuid
import json
from datetime import datetime

from src.database import get_db
from src.redis_client import redis_client
from src.session.models import Session
from src.session.schemas import SessionState, ConversationStage
from src.workflow.models import Workflow
from src.workflow.schemas import (
    WorkflowReviewRequest,
    WorkflowReviewResponse,
    WorkflowVisualization,
    WorkflowData,
)
from src.workflow.synthesizer import get_synthesizer
from src.workflow.visualizer import generate_mermaid_diagram, generate_text_summary

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/{session_id}", response_model=WorkflowReviewResponse)
async def get_workflow(session_id: str, db: DBSession = Depends(get_db)):
    """
    Get the workflow for a session.
    If not yet generated, creates it from session state.
    """

    # Check if workflow already exists
    workflow = db.query(Workflow).filter(Workflow.session_id == session_id).first()

    if workflow:
        # Return existing workflow
        workflow_data = WorkflowData(**json.loads(workflow.workflow_json))

        return WorkflowReviewResponse(
            session_id=session_id,
            workflow=workflow_data,
            mermaid_diagram=workflow.mermaid_diagram or "",
            is_final=workflow.is_approved,
        )

    # Generate new workflow from session state
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found or expired",
        )

    session_state = SessionState(**session_data)

    # Synthesize workflow
    synthesizer = get_synthesizer()
    workflow_data = synthesizer.synthesize(session_state)

    # Generate visualization
    mermaid = generate_mermaid_diagram(workflow_data)

    # Save to database
    db_workflow = Workflow(
        id=str(uuid.uuid4()),
        session_id=session_id,
        agent_type=workflow_data.agent_type,
        goals=workflow_data.goals,
        tone=workflow_data.tone,
        use_tools=workflow_data.use_tools,
        workflow_json=workflow_data.model_dump_json(),
        mermaid_diagram=mermaid,
        is_approved=False,
    )
    db.add(db_workflow)
    db.commit()

    return WorkflowReviewResponse(
        session_id=session_id,
        workflow=workflow_data,
        mermaid_diagram=mermaid,
        is_final=False,
    )


@router.post("/{session_id}/review", response_model=WorkflowReviewResponse)
async def review_workflow(
    session_id: str,
    review: WorkflowReviewRequest,
    db: DBSession = Depends(get_db),
):
    """
    Review and optionally approve workflow.
    If changes requested, workflow can be regenerated.
    """

    workflow = db.query(Workflow).filter(Workflow.session_id == session_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow for session {session_id} not found",
        )

    if review.approved:
        # User approved the workflow
        workflow.is_approved = True
        workflow.approved_at = datetime.utcnow()
        db.commit()

        workflow_data = WorkflowData(**json.loads(workflow.workflow_json))

        return WorkflowReviewResponse(
            session_id=session_id,
            workflow=workflow_data,
            mermaid_diagram=workflow.mermaid_diagram or "",
            is_final=True,
        )
    else:
        # User requested changes
        # Return current workflow with requested changes noted
        workflow_data = WorkflowData(**json.loads(workflow.workflow_json))

        return WorkflowReviewResponse(
            session_id=session_id,
            workflow=workflow_data,
            mermaid_diagram=workflow.mermaid_diagram or "",
            is_final=False,
        )


@router.get("/{session_id}/visualize", response_model=WorkflowVisualization)
async def visualize_workflow(session_id: str, db: DBSession = Depends(get_db)):
    """
    Get visual representations of the workflow.
    If workflow doesn't exist yet, creates it from session state.
    """

    workflow = db.query(Workflow).filter(Workflow.session_id == session_id).first()

    if not workflow:
        # Try to create workflow from session state (fallback)
        session_data = redis_client.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found or expired",
            )

        session_state = SessionState(**session_data)

        # Only create if in review stage or later
        if session_state.stage not in [
            ConversationStage.REVIEWING_WORKFLOW,
            ConversationStage.FINALIZING,
            ConversationStage.COMPLETED,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow not ready yet. Current stage: {session_state.stage}",
            )

        # Synthesize and save workflow
        synthesizer = get_synthesizer()
        workflow_data = synthesizer.synthesize(session_state)
        mermaid = generate_mermaid_diagram(workflow_data)

        workflow = Workflow(
            id=str(uuid.uuid4()),
            session_id=session_id,
            agent_type=workflow_data.agent_type,
            goals=workflow_data.goals,
            tone=workflow_data.tone,
            use_tools=workflow_data.use_tools,
            workflow_json=workflow_data.model_dump_json(),
            mermaid_diagram=mermaid,
            is_approved=False,
        )
        db.add(workflow)
        db.commit()

    workflow_data = WorkflowData(**json.loads(workflow.workflow_json))

    # Generate visualizations
    mermaid = workflow.mermaid_diagram or generate_mermaid_diagram(workflow_data)
    text_summary = generate_text_summary(workflow_data)

    return WorkflowVisualization(
        mermaid_diagram=mermaid,
        json_structure=workflow_data.model_dump(),
        summary=text_summary,
    )


@router.post("/{session_id}/regenerate", response_model=WorkflowReviewResponse)
async def regenerate_workflow(session_id: str, db: DBSession = Depends(get_db)):
    """
    Regenerate workflow from current session state.
    Useful after user makes changes to agent configuration.
    """

    # Get session state
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found or expired",
        )

    session_state = SessionState(**session_data)

    # Synthesize new workflow
    synthesizer = get_synthesizer()
    workflow_data = synthesizer.synthesize(session_state)

    # Generate visualization
    mermaid = generate_mermaid_diagram(workflow_data)

    # Update or create workflow in database
    workflow = db.query(Workflow).filter(Workflow.session_id == session_id).first()

    if workflow:
        # Update existing
        workflow.agent_type = workflow_data.agent_type
        workflow.goals = workflow_data.goals
        workflow.tone = workflow_data.tone
        workflow.use_tools = workflow_data.use_tools
        workflow.workflow_json = workflow_data.model_dump_json()
        workflow.mermaid_diagram = mermaid
        workflow.is_approved = False  # Reset approval
        workflow.updated_at = datetime.utcnow()
    else:
        # Create new
        workflow = Workflow(
            id=str(uuid.uuid4()),
            session_id=session_id,
            agent_type=workflow_data.agent_type,
            goals=workflow_data.goals,
            tone=workflow_data.tone,
            use_tools=workflow_data.use_tools,
            workflow_json=workflow_data.model_dump_json(),
            mermaid_diagram=mermaid,
            is_approved=False,
        )
        db.add(workflow)

    db.commit()

    return WorkflowReviewResponse(
        session_id=session_id,
        workflow=workflow_data,
        mermaid_diagram=mermaid,
        is_final=False,
    )
