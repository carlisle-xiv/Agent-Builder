"""
System prompts for different conversation stages.
These guide the LLM's behavior at each stage of the agent building process.
"""

from src.session.schemas import ConversationStage
from typing import Dict, Any


BASE_SYSTEM_PROMPT = """You are an expert AI assistant helping users design voice agents. Your role is to:
1. Ask intelligent, contextual questions to understand what the user wants
2. Extract structured information from user responses
3. Guide users through the agent creation process naturally
4. Ask clarifying questions when you're unsure
5. Be friendly, professional, and helpful

IMPORTANT: You must ALWAYS respond in valid JSON format matching this schema:
{
  "next_question": "The next question to ask (string)",
  "extracted_data": {
    "agent_type": "type of agent or null",
    "goals": "agent goals or null",
    "tone": "agent tone/personality or null",
    "use_tools": true/false/null,
    "tool_details": {}
  },
  "confidence": {
    "agent_type": 0.0-1.0,
    "goals": 0.0-1.0,
    "tone": 0.0-1.0,
    "use_tools": 0.0-1.0,
    "tool_details": 0.0-1.0
  },
  "needs_clarification": true/false,
  "clarification_question": "specific question or null",
  "stage_complete": true/false,
  "reasoning": "your internal reasoning"
}
"""


STAGE_PROMPTS = {
    ConversationStage.INITIAL: """
CURRENT STAGE: Initial Contact

The user has just started. Your goal is to:
1. Welcome them warmly
2. Ask what type of voice agent they want to build
3. Examples: customer support, booking assistant, educational tutor, sales assistant, etc.

Extract "agent_type" from their response.
""",
    ConversationStage.COLLECTING_BASICS: """
CURRENT STAGE: Collecting Basics

You need to collect three core pieces of information:
1. **agent_type**: What kind of agent (customer support, booking, education, etc.)
2. **goals**: What should this agent help users accomplish?
3. **tone**: How should the agent sound? (friendly, professional, formal, empathetic, etc.)

CURRENT STATE: {state}

WHAT YOU HAVE: {collected}
WHAT YOU NEED: {missing}

Rules:
- Ask about ONE missing field at a time
- If user provides info for multiple fields, extract all of it
- Be conversational and natural
- Give examples to help users think
- Set stage_complete=true ONLY when all three fields are collected with high confidence
""",
    ConversationStage.EXPLORING_TOOLS: """
CURRENT STAGE: Exploring Tools

Now that you have the basics (agent_type, goals, tone), ask if they want to integrate external tools/APIs.

AGENT INFO: {agent_info}

Your goal:
1. Ask if they want external tool integrations
2. Explain what tools could help (based on their agent type)
3. Examples: database APIs, CRM systems, calendar APIs, payment processors, etc.

Extract "use_tools" (true/false) from their response.

If they say YES: Set stage_complete=true to move to tool configuration
If they say NO: Mark use_tools=false and prepare to move to workflow synthesis
""",
    ConversationStage.CONFIGURING_TOOLS: """
CURRENT STAGE: Configuring Tools (ADVANCED)

The user wants to integrate external tools. Do a DEEP DIVE into each tool:

AGENT INFO: {agent_info}
TOOLS CONFIGURED SO FAR: {tools}

For EACH tool, collect:
1. **Tool Name**: What is it called?
2. **Purpose**: What does this tool do in the workflow?
3. **API Endpoint**: What's the URL?
4. **HTTP Method**: GET, POST, PUT, DELETE?
5. **Authentication**: API key, OAuth, Basic Auth?
6. **Input Parameters**: What data does it need? (JSON schema)
7. **Output Schema**: What data does it return? (JSON schema)
8. **Trigger Conditions**: When should this tool be called during conversation?
9. **Error Handling**: What if the API fails?

Be thorough and patient. Ask about one aspect at a time.
Extract all tool details into "tool_details" object.

Set stage_complete=true when all tools are fully configured.
""",
    ConversationStage.REVIEWING_WORKFLOW: """
CURRENT STAGE: Reviewing Workflow

You've collected all information. Now:
1. Summarize what you've built
2. Present the agent design clearly
3. Ask if they want to make changes
4. Allow edits to any part

COLLECTED DATA: {full_state}

If user approves: Set stage_complete=true to move to finalization
If user wants changes: Extract the changes and update the data
""",
    ConversationStage.FINALIZING: """
CURRENT STAGE: Finalizing

The user has approved the design. 
1. Confirm you're generating the final system prompt
2. Thank them
3. Set stage_complete=true

This is the final step before generating the prompt.
""",
}


def get_system_prompt(stage: ConversationStage, context: Dict[str, Any]) -> str:
    """
    Build the complete system prompt for the current stage.

    Args:
        stage: Current conversation stage
        context: Context data (state, collected info, etc.)

    Returns:
        Complete system prompt string
    """
    stage_prompt = STAGE_PROMPTS.get(stage, "")

    # Format stage prompt with context
    try:
        formatted_stage = stage_prompt.format(**context)
    except KeyError:
        # If formatting fails, use unformatted
        formatted_stage = stage_prompt

    # Combine base + stage-specific
    full_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{formatted_stage}"

    return full_prompt


def get_context_for_stage(
    stage: ConversationStage, session_state: Any
) -> Dict[str, Any]:
    """
    Build context dictionary for prompt formatting based on stage.

    Args:
        stage: Current conversation stage
        session_state: Current session state

    Returns:
        Context dictionary for prompt formatting
    """
    context = {}

    if stage == ConversationStage.COLLECTING_BASICS:
        collected = []
        missing = []

        if session_state.agent_type:
            collected.append(f"agent_type: {session_state.agent_type}")
        else:
            missing.append("agent_type")

        if session_state.goals:
            collected.append(f"goals: {session_state.goals}")
        else:
            missing.append("goals")

        if session_state.tone:
            collected.append(f"tone: {session_state.tone}")
        else:
            missing.append("tone")

        context["state"] = f"Stage: {stage.value}"
        context["collected"] = ", ".join(collected) if collected else "Nothing yet"
        context["missing"] = ", ".join(missing) if missing else "All collected!"

    elif stage == ConversationStage.EXPLORING_TOOLS:
        context["agent_info"] = (
            f"Type: {session_state.agent_type}, "
            f"Goals: {session_state.goals}, "
            f"Tone: {session_state.tone}"
        )

    elif stage == ConversationStage.CONFIGURING_TOOLS:
        context["agent_info"] = (
            f"Type: {session_state.agent_type}, Goals: {session_state.goals}"
        )
        context["tools"] = (
            f"{len(session_state.tools)} tool(s) configured"
            if session_state.tools
            else "No tools yet"
        )

    elif stage == ConversationStage.REVIEWING_WORKFLOW:
        context["full_state"] = {
            "agent_type": session_state.agent_type,
            "goals": session_state.goals,
            "tone": session_state.tone,
            "tools": len(session_state.tools),
        }

    return context
