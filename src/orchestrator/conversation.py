"""
Conversation Orchestrator - The brain of the agent builder.
Coordinates LLM calls, data extraction, and stage progression.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.session.schemas import SessionState, ConversationStage, ToolConfigSchema
from src.llm.client import get_llm_client
from src.llm.prompts import get_system_prompt, get_context_for_stage
from src.llm.schemas import LLMResponse
from src.orchestrator.stages import determine_next_stage, is_stage_complete
from src.workflow.synthesizer import get_synthesizer
from src.workflow.visualizer import generate_text_summary


class ConversationOrchestrator:
    """
    Main orchestrator that processes user messages and generates AI responses.
    """

    def __init__(self):
        self.llm_client = get_llm_client()

    async def process_message(
        self, session_state: SessionState, user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate AI response.

        This is the main entry point for the orchestrator.

        Args:
            session_state: Current session state
            user_message: User's message

        Returns:
            Dictionary with:
                - ai_response: The AI's response
                - updated_state: Updated session state
                - stage_changed: Whether stage progressed
                - is_complete: Whether conversation is done
        """

        # 1. Build context for LLM
        context = get_context_for_stage(session_state.stage, session_state)

        # 2. Get system prompt for current stage
        system_prompt = get_system_prompt(session_state.stage, context)

        # 3. Call LLM
        llm_response = await self.llm_client.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=session_state.conversation_history,
            stage=session_state.stage,
        )

        # 4. Update session state with extracted data
        updated_state = self._update_session_state(session_state, llm_response)

        # 5. Determine if we should progress to next stage
        original_stage = session_state.stage
        new_stage, transition_reason = determine_next_stage(
            updated_state.stage, updated_state
        )

        stage_changed = new_stage != original_stage

        if stage_changed:
            print(f"📊 Stage transition: {original_stage} → {new_stage}")
            print(f"   Reason: {transition_reason}")
            updated_state.stage = new_stage

            # 5a. Generate workflow when entering REVIEWING_WORKFLOW stage
            if new_stage == ConversationStage.REVIEWING_WORKFLOW:
                workflow_summary = await self._generate_workflow_summary(updated_state)
                # Store workflow summary in state for review
                if updated_state.workflow is None:
                    updated_state.workflow = {"summary": workflow_summary}

        # 6. Update timestamp
        updated_state.updated_at = datetime.utcnow()

        # 7. Determine final AI response
        ai_response = self._build_ai_response(
            llm_response, stage_changed, new_stage, updated_state
        )

        # 8. Check if conversation is complete
        is_complete = updated_state.stage == ConversationStage.COMPLETED

        return {
            "ai_response": ai_response,
            "updated_state": updated_state,
            "stage_changed": stage_changed,
            "is_complete": is_complete,
            "new_stage": new_stage if stage_changed else None,
        }

    def _update_session_state(
        self, session_state: SessionState, llm_response: LLMResponse
    ) -> SessionState:
        """
        Update session state with extracted data from LLM.

        Args:
            session_state: Current state
            llm_response: LLM's structured response

        Returns:
            Updated session state
        """

        extracted = llm_response.extracted_data

        # Update agent basics
        if extracted.agent_type and llm_response.confidence.agent_type > 0.6:
            session_state.agent_type = extracted.agent_type
            if "agent_type" not in session_state.collected_fields:
                session_state.collected_fields.append("agent_type")

        if extracted.goals and llm_response.confidence.goals > 0.6:
            session_state.goals = extracted.goals
            if "goals" not in session_state.collected_fields:
                session_state.collected_fields.append("goals")

        if extracted.tone and llm_response.confidence.tone > 0.6:
            session_state.tone = extracted.tone
            if "tone" not in session_state.collected_fields:
                session_state.collected_fields.append("tone")

        # Update detailed specifications
        if extracted.target_users:
            session_state.target_users = extracted.target_users
        if extracted.greeting_style:
            session_state.greeting_style = extracted.greeting_style
        if extracted.conversation_flow:
            session_state.conversation_flow = extracted.conversation_flow
        if extracted.example_interactions:
            session_state.example_interactions.extend(extracted.example_interactions)
        if extracted.constraints:
            session_state.constraints.extend(extracted.constraints)
        if extracted.edge_cases:
            session_state.edge_cases.extend(extracted.edge_cases)
        if extracted.escalation_rules:
            session_state.escalation_rules = extracted.escalation_rules
        if extracted.success_criteria:
            session_state.success_criteria = extracted.success_criteria
        if extracted.brand_voice:
            session_state.brand_voice = extracted.brand_voice
        if extracted.verbosity_level:
            session_state.verbosity_level = extracted.verbosity_level
        if extracted.additional_notes:
            if session_state.additional_notes:
                session_state.additional_notes += f"\n{extracted.additional_notes}"
            else:
                session_state.additional_notes = extracted.additional_notes

        # Update tool usage
        if extracted.use_tools is not None and llm_response.confidence.use_tools > 0.6:
            session_state.use_tools = extracted.use_tools
            if "use_tools" not in session_state.collected_fields:
                session_state.collected_fields.append("use_tools")

        # Update tool details (ONLY for CONFIGURING_TOOLS stage)
        if extracted.tool_details and llm_response.confidence.tool_details > 0.5:
            # Only process tool details if we're in the configuration stage
            if session_state.stage == ConversationStage.CONFIGURING_TOOLS:
                try:
                    # Create or update tool configuration
                    tool_config = ToolConfigSchema(**extracted.tool_details)
                    session_state.tools.append(tool_config)
                    if "tools" not in session_state.collected_fields:
                        session_state.collected_fields.append("tools")
                except Exception as e:
                    print(f"⚠️  Failed to parse tool config: {e}")
                    # Skip invalid tool data - will ask again

        return session_state

    async def _generate_workflow_summary(self, session_state: SessionState) -> str:
        """
        Generate workflow summary when entering review stage.

        Args:
            session_state: Current session state

        Returns:
            Workflow summary text
        """
        try:
            synthesizer = get_synthesizer()
            workflow_data = synthesizer.synthesize(session_state)
            summary = generate_text_summary(workflow_data)
            return summary
        except Exception as e:
            print(f"⚠️  Error generating workflow: {e}")
            return "Error generating workflow summary"

    def _build_ai_response(
        self,
        llm_response: LLMResponse,
        stage_changed: bool,
        new_stage: ConversationStage,
        session_state: SessionState = None,
    ) -> str:
        """
        Build the final AI response to send to user.

        Args:
            llm_response: LLM's response
            stage_changed: Whether stage progressed
            new_stage: New stage if changed

        Returns:
            Final AI response string
        """

        response_parts = []

        # Add stage transition message if needed
        if stage_changed:
            transition_messages = {
                ConversationStage.COLLECTING_BASICS: "",  # Silent transition
                ConversationStage.EXPLORING_TOOLS: "\n\nGreat! Now let's talk about integrations.",
                ConversationStage.CONFIGURING_TOOLS: "\n\nPerfect! Let's configure your tools.",
                ConversationStage.REVIEWING_WORKFLOW: "\n\nExcellent! Let me summarize what we've built.",
                ConversationStage.FINALIZING: "\n\nPerfect! Generating your agent configuration...",
                ConversationStage.COMPLETED: "\n\n✅ Your voice agent is ready!",
            }
            transition_msg = transition_messages.get(new_stage, "")
            if transition_msg:
                response_parts.append(transition_msg)

        # Add workflow summary if in review stage
        if new_stage == ConversationStage.REVIEWING_WORKFLOW and session_state:
            if session_state.workflow and session_state.workflow.get("summary"):
                response_parts.append("\n📋 Here's your agent workflow:\n")
                response_parts.append(session_state.workflow["summary"])
                response_parts.append(
                    "\nDoes this look good to you? Would you like to make any changes?"
                )
                return "\n".join(response_parts)

        # Add clarification question if needed
        if llm_response.needs_clarification and llm_response.clarification_question:
            response_parts.append(llm_response.clarification_question)
        else:
            # Add main question
            response_parts.append(llm_response.next_question)

        return "\n".join(response_parts)

    async def generate_initial_question(self) -> str:
        """
        Generate the initial question when session is created.

        Returns:
            Initial greeting and question
        """
        return (
            "Hello! I'm here to help you design a voice agent. "
            "To get started, what kind of voice agent would you like to create? "
            "For example, are you building a customer support agent, a booking assistant, "
            "an educational tutor, or something else?"
        )


# Global orchestrator instance
_orchestrator: Optional[ConversationOrchestrator] = None


def get_orchestrator() -> ConversationOrchestrator:
    """
    Get or create global orchestrator instance.

    Returns:
        ConversationOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
    return _orchestrator
