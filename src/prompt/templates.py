"""
Prompt templates for different platforms and formats.
"""

from typing import Dict, Any, List


def generate_elevenlabs_prompt(
    agent_type: str,
    goals: str,
    tone: str,
    use_tools: bool,
    tools: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate ElevenLabs voice agent system prompt.

    ElevenLabs requires concise, conversational prompts focused on voice interaction.
    """

    prompt_parts = []

    # Role definition
    prompt_parts.append(
        f"You are a {tone} {agent_type} voice agent designed to {goals}."
    )

    # Voice-specific instructions
    prompt_parts.append(
        "\nCONVERSATION STYLE:\n"
        f"- Maintain a {tone} tone throughout all interactions\n"
        "- Keep responses concise and natural for voice conversation\n"
        "- Use conversational language, avoid overly formal or robotic speech\n"
        "- Speak clearly and pause appropriately for user responses\n"
        "- Confirm understanding before taking actions"
    )

    # Goals and objectives
    prompt_parts.append(
        f"\nYOUR PRIMARY GOALS:\n"
        f"{goals}\n"
        "\nAlways prioritize helping the user achieve their goals efficiently."
    )

    # Tool integration
    if use_tools and tools:
        prompt_parts.append(
            "\nAVAILABLE TOOLS:\n"
            "You have access to the following tools to assist users:\n"
        )
        for tool in tools:
            tool_name = tool.get("name", "Unknown Tool")
            tool_desc = tool.get("description", "")
            prompt_parts.append(f"- {tool_name}: {tool_desc}")

        prompt_parts.append(
            "\nWhen using tools:\n"
            "- Clearly explain what you're doing\n"
            "- Gather all required information before calling tools\n"
            "- Confirm results with the user"
        )

    # Best practices
    prompt_parts.append(
        "\nBEST PRACTICES:\n"
        "- Ask clarifying questions when needed\n"
        "- Provide helpful suggestions proactively\n"
        "- Handle errors gracefully and offer alternatives\n"
        "- End conversations politely and offer further assistance"
    )

    return "\n".join(prompt_parts)


def generate_openai_assistant_prompt(
    agent_type: str,
    goals: str,
    tone: str,
    use_tools: bool,
    tools: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate OpenAI Assistant API system prompt.

    OpenAI Assistants support more structured instructions and tool calling.
    """

    prompt_parts = []

    # Role and context
    prompt_parts.append(
        f"# {agent_type.title()} Assistant\n\n"
        f"You are an AI assistant specialized in {agent_type}. "
        f"Your primary objective is to {goals}.\n"
    )

    # Personality and tone
    prompt_parts.append(
        f"## Personality\n"
        f"Communicate with a {tone} demeanor. "
        "Be helpful, accurate, and user-focused in all interactions.\n"
    )

    # Capabilities
    prompt_parts.append(
        f"## Capabilities\n"
        f"Your main responsibilities include:\n"
        f"- {goals}\n"
        "- Providing accurate and helpful information\n"
        "- Guiding users through processes step-by-step\n"
        "- Handling edge cases and errors professionally\n"
    )

    # Tool usage
    if use_tools and tools:
        prompt_parts.append("## Tools\nYou have access to the following tools:\n")
        for tool in tools:
            tool_name = tool.get("name", "Unknown Tool")
            tool_desc = tool.get("description", "")
            prompt_parts.append(f"### {tool_name}\n{tool_desc}\n")

        prompt_parts.append(
            "When using tools:\n"
            "1. Validate all required parameters before calling\n"
            "2. Handle tool errors gracefully\n"
            "3. Explain tool results to the user in simple terms\n"
        )

    # Guidelines
    prompt_parts.append(
        "## Guidelines\n"
        "- Always prioritize user satisfaction and goal completion\n"
        "- Ask for clarification when information is ambiguous\n"
        "- Provide clear, actionable responses\n"
        "- Maintain context throughout the conversation\n"
        "- Be proactive in suggesting next steps"
    )

    return "\n".join(prompt_parts)


def generate_generic_prompt(
    agent_type: str,
    goals: str,
    tone: str,
    use_tools: bool,
    tools: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate generic system prompt that works across platforms.

    Flexible format suitable for most LLM platforms.
    """

    prompt_parts = []

    # Core identity
    prompt_parts.append(
        f"You are a {tone} {agent_type} assistant. Your purpose is to {goals}."
    )

    # Behavioral guidelines
    prompt_parts.append(
        f"\nKey Characteristics:\n"
        f"- Tone: {tone}\n"
        f"- Focus: {goals}\n"
        "- Approach: Helpful, accurate, and user-centric\n"
    )

    # Operational guidelines
    prompt_parts.append(
        "\nOperational Guidelines:\n"
        "1. Listen carefully to user needs and respond appropriately\n"
        "2. Provide clear, concise, and accurate information\n"
        "3. Ask clarifying questions when necessary\n"
        "4. Guide users step-by-step through complex processes\n"
        "5. Handle errors and edge cases gracefully\n"
    )

    # Tool information
    if use_tools and tools:
        prompt_parts.append(
            f"\nAvailable Tools: {len(tools)}\n"
            "You have access to specialized tools to assist users:\n"
        )
        for i, tool in enumerate(tools, 1):
            tool_name = tool.get("name", f"Tool {i}")
            tool_desc = tool.get("description", "No description")
            prompt_parts.append(f"{i}. {tool_name} - {tool_desc}")

        prompt_parts.append(
            "\nUse these tools when appropriate to better serve the user."
        )

    # Success criteria
    prompt_parts.append(
        "\nSuccess Metrics:\n"
        "- User achieves their goals efficiently\n"
        "- Communication is clear and helpful\n"
        "- User feels satisfied with the interaction\n"
    )

    return "\n".join(prompt_parts)


def generate_anthropic_prompt(
    agent_type: str,
    goals: str,
    tone: str,
    use_tools: bool,
    tools: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate Anthropic Claude system prompt.

    Claude benefits from clear role definition and structured instructions.
    """

    prompt_parts = []

    # Role definition
    prompt_parts.append(
        f"You are Claude, configured as a {tone} {agent_type} assistant. "
        f"Your core mission is to {goals}."
    )

    # Competencies
    prompt_parts.append(
        f"\n<competencies>\n"
        f"- Primary goal: {goals}\n"
        f"- Communication style: {tone}\n"
        "- Core strength: Understanding user needs and providing actionable assistance\n"
        "- Special focus: Maintaining context and ensuring user satisfaction\n"
        "</competencies>"
    )

    # Instructions
    prompt_parts.append(
        "\n<instructions>\n"
        "When interacting with users:\n"
        "1. Begin by understanding their specific needs\n"
        "2. Provide clear, structured responses\n"
        "3. Use examples when helpful\n"
        "4. Confirm understanding before proceeding with actions\n"
        "5. Adapt your communication style to user preferences\n"
        "</instructions>"
    )

    # Tool configuration
    if use_tools and tools:
        prompt_parts.append("\n<tools>\nYou have access to these tools:\n")
        for tool in tools:
            tool_name = tool.get("name", "Unknown")
            tool_desc = tool.get("description", "")
            prompt_parts.append(f'\n<tool name="{tool_name}">\n{tool_desc}\n</tool>')
        prompt_parts.append(
            "\nUse tools thoughtfully and explain your actions to the user.\n</tools>"
        )

    # Quality standards
    prompt_parts.append(
        "\n<quality_standards>\n"
        "- Accuracy: Provide correct and up-to-date information\n"
        "- Clarity: Communicate in clear, understandable language\n"
        f"- Tone: Maintain {tone} demeanor consistently\n"
        "- Efficiency: Help users achieve goals with minimal friction\n"
        "</quality_standards>"
    )

    return "\n".join(prompt_parts)


def generate_openai_chat_prompt(
    agent_type: str,
    goals: str,
    tone: str,
    use_tools: bool,
    tools: List[Dict[str, Any]] = None,
) -> str:
    """
    Generate OpenAI Chat Completion system prompt.

    Optimized for GPT-4 and GPT-3.5 chat models.
    """

    prompt_parts = []

    # System identity
    prompt_parts.append(
        f"You are a {tone} AI assistant specializing in {agent_type}. "
        f"Your primary function is to {goals}."
    )

    # Core responsibilities
    prompt_parts.append(
        f"\nCore Responsibilities:\n"
        f"• {goals}\n"
        "• Providing accurate, helpful information\n"
        "• Guiding users through processes clearly\n"
        "• Maintaining a consistent, helpful presence\n"
    )

    # Communication style
    prompt_parts.append(
        f"\nCommunication Style:\n"
        f"• Tone: {tone}\n"
        "• Approach: Clear, concise, and actionable\n"
        "• Format: Structured when appropriate, conversational when natural\n"
    )

    # Tool integration
    if use_tools and tools:
        prompt_parts.append("\nIntegrated Tools:\n")
        for tool in tools:
            tool_name = tool.get("name", "Unknown Tool")
            tool_desc = tool.get("description", "")
            prompt_parts.append(f"• {tool_name}: {tool_desc}")

        prompt_parts.append(
            "\nTool Usage Protocol:\n"
            "1. Identify when a tool is needed\n"
            "2. Gather required information from user\n"
            "3. Execute tool with proper parameters\n"
            "4. Interpret and communicate results\n"
        )

    # Best practices
    prompt_parts.append(
        "\nBest Practices:\n"
        "• Ask clarifying questions to avoid assumptions\n"
        "• Break down complex tasks into manageable steps\n"
        "• Provide examples when helpful\n"
        "• Acknowledge limitations and offer alternatives when needed\n"
        "• End interactions with clear next steps or conclusions\n"
    )

    return "\n".join(prompt_parts)


# Template mapping
PROMPT_GENERATORS = {
    "elevenlabs": generate_elevenlabs_prompt,
    "openai_assistant": generate_openai_assistant_prompt,
    "openai_chat": generate_openai_chat_prompt,
    "anthropic": generate_anthropic_prompt,
    "generic": generate_generic_prompt,
}
