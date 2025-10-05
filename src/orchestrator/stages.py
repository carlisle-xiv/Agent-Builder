"""
Stage management logic - determines when to progress to next stage.
Implements "strict but flexible" progression rules.
"""

from src.session.schemas import SessionState, ConversationStage
from typing import Tuple, Optional


def is_stage_complete(session_state: SessionState) -> bool:
    """
    Check if current stage is complete and ready to progress.

    Args:
        session_state: Current session state

    Returns:
        True if stage is complete
    """
    stage = session_state.stage

    if stage == ConversationStage.INITIAL:
        # Initial is complete after first exchange
        return len(session_state.conversation_history) > 0

    elif stage == ConversationStage.COLLECTING_BASICS:
        # Need all three: agent_type, goals, tone
        return all(
            [
                session_state.agent_type is not None,
                session_state.goals is not None,
                session_state.tone is not None,
            ]
        )

    elif stage == ConversationStage.EXPLORING_TOOLS:
        # Complete when user has answered about tool usage
        return session_state.use_tools is not None

    elif stage == ConversationStage.CONFIGURING_TOOLS:
        # Complete when user confirms tools are configured
        # (or use_tools=False, should have skipped this stage)
        if session_state.use_tools is False:
            return True  # Skip if not using tools

        # If using tools, need at least one tool configured
        return len(session_state.tools) > 0

    elif stage == ConversationStage.REVIEWING_WORKFLOW:
        # Complete when user approves
        # This will be set by LLM when user confirms
        return False  # Controlled by LLM

    elif stage == ConversationStage.FINALIZING:
        return False  # This is the last stage before completion

    elif stage == ConversationStage.COMPLETED:
        return True  # Already done

    return False


def determine_next_stage(
    current_stage: ConversationStage, session_state: SessionState
) -> Tuple[ConversationStage, Optional[str]]:
    """
    Determine the next stage based on current state.
    Returns (next_stage, reason)

    Args:
        current_stage: Current conversation stage
        session_state: Current session state

    Returns:
        Tuple of (next_stage, reason_for_transition)
    """

    if not is_stage_complete(session_state):
        return current_stage, None  # Stay in current stage

    # Stage progression logic
    if current_stage == ConversationStage.INITIAL:
        return (
            ConversationStage.COLLECTING_BASICS,
            "Moving to collect agent basics",
        )

    elif current_stage == ConversationStage.COLLECTING_BASICS:
        return (
            ConversationStage.EXPLORING_TOOLS,
            "Basics collected, exploring tool needs",
        )

    elif current_stage == ConversationStage.EXPLORING_TOOLS:
        if session_state.use_tools is True:
            return (
                ConversationStage.CONFIGURING_TOOLS,
                "User wants tools, configuring them",
            )
        else:
            # Skip tool configuration, go straight to review
            return (
                ConversationStage.REVIEWING_WORKFLOW,
                "No tools needed, reviewing workflow",
            )

    elif current_stage == ConversationStage.CONFIGURING_TOOLS:
        return (
            ConversationStage.REVIEWING_WORKFLOW,
            "Tools configured, reviewing workflow",
        )

    elif current_stage == ConversationStage.REVIEWING_WORKFLOW:
        return ConversationStage.FINALIZING, "Workflow approved, finalizing"

    elif current_stage == ConversationStage.FINALIZING:
        return ConversationStage.COMPLETED, "Process complete"

    # Default: stay in current stage
    return current_stage, None


def allow_early_progression(
    current_stage: ConversationStage, session_state: SessionState
) -> bool:
    """
    Check if we should allow early progression (flexible rule).
    E.g., user provides all info in one message.

    Args:
        current_stage: Current stage
        session_state: Session state

    Returns:
        True if early progression is allowed
    """

    # If in COLLECTING_BASICS and user has provided everything
    if current_stage == ConversationStage.COLLECTING_BASICS:
        # If user mentioned tools in their initial message
        if all(
            [
                session_state.agent_type,
                session_state.goals,
                session_state.tone,
            ]
        ):
            # Allow early progression
            return True

    # Add more flexible rules as needed
    return False
