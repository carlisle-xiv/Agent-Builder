"""
Workflow Synthesizer - Compiles session data into structured workflow.
"""

from typing import Optional, List
import uuid

from src.session.schemas import SessionState, ToolConfigSchema
from src.workflow.schemas import (
    WorkflowData,
    WorkflowNode,
    WorkflowEdge,
    NodeType,
)
from src.workflow.visualizer import generate_mermaid_diagram


class WorkflowSynthesizer:
    """
    Synthesizes a workflow from collected session data.
    Creates a structured representation of the voice agent's behavior.
    """

    def synthesize(self, session_state: SessionState) -> WorkflowData:
        """
        Create a workflow from session state.

        Args:
            session_state: Current session state with collected data

        Returns:
            Complete workflow representation
        """

        # Create workflow data structure
        workflow = WorkflowData(
            session_id=session_state.session_id,
            agent_type=session_state.agent_type or "general",
            goals=session_state.goals or "",
            tone=session_state.tone or "professional",
            use_tools=session_state.use_tools or False,
            tools=[tool.model_dump() for tool in session_state.tools],
        )

        # Build workflow nodes and edges
        nodes, edges = self._build_workflow_graph(session_state)
        workflow.nodes = nodes
        workflow.edges = edges

        # Generate description
        workflow.description = self._generate_workflow_description(session_state)

        return workflow

    def _build_workflow_graph(
        self, session_state: SessionState
    ) -> tuple[List[WorkflowNode], List[WorkflowEdge]]:
        """
        Build the workflow graph (nodes and edges).

        Args:
            session_state: Session state

        Returns:
            Tuple of (nodes, edges)
        """

        nodes: List[WorkflowNode] = []
        edges: List[WorkflowEdge] = []

        # 1. Start Node
        start_node = WorkflowNode(
            id="start",
            type=NodeType.START,
            label="Start",
            description="Conversation begins",
            position={"x": 100, "y": 50},
        )
        nodes.append(start_node)

        # 2. Greeting Node
        greeting_node = WorkflowNode(
            id="greeting",
            type=NodeType.GREETING,
            label="Greet User",
            description=f"Greet user with {session_state.tone} tone",
            config={
                "tone": session_state.tone,
                "greeting_template": self._generate_greeting(session_state),
            },
            position={"x": 100, "y": 150},
        )
        nodes.append(greeting_node)
        edges.append(WorkflowEdge(source="start", target="greeting"))

        # 3. Intent Detection Node
        intent_node = WorkflowNode(
            id="intent_detection",
            type=NodeType.INTENT_DETECTION,
            label="Detect User Intent",
            description=f"Understand user needs related to: {session_state.goals}",
            config={"expected_intents": self._extract_intents(session_state)},
            position={"x": 100, "y": 250},
        )
        nodes.append(intent_node)
        edges.append(WorkflowEdge(source="greeting", target="intent_detection"))

        # 4. Add tool nodes if tools are configured
        if session_state.use_tools and session_state.tools:
            tool_nodes = self._build_tool_nodes(session_state.tools)
            nodes.extend(tool_nodes)

            # Create conditional edges to tools
            for i, tool_node in enumerate(tool_nodes):
                tool_config = session_state.tools[i]
                edges.append(
                    WorkflowEdge(
                        source="intent_detection",
                        target=tool_node.id,
                        label=f"Use {tool_config.name}",
                        condition=tool_config.usage_context
                        or f"When user needs {tool_config.name}",
                    )
                )

                # Tool to response
                edges.append(
                    WorkflowEdge(
                        source=tool_node.id,
                        target="response",
                        label="Process result",
                    )
                )
        else:
            # No tools - direct to response
            edges.append(WorkflowEdge(source="intent_detection", target="response"))

        # 5. Response Node
        response_node = WorkflowNode(
            id="response",
            type=NodeType.RESPONSE,
            label="Generate Response",
            description=f"Respond in {session_state.tone} tone addressing: {session_state.goals}",
            config={
                "tone": session_state.tone,
                "goals": session_state.goals,
                "response_guidelines": self._generate_response_guidelines(
                    session_state
                ),
            },
            position={"x": 100, "y": 450},
        )
        nodes.append(response_node)

        # 6. Condition Node (Continue or End?)
        condition_node = WorkflowNode(
            id="continue_check",
            type=NodeType.CONDITION,
            label="More Questions?",
            description="Check if user has more questions",
            config={"check": "User has more questions"},
            position={"x": 100, "y": 550},
        )
        nodes.append(condition_node)
        edges.append(WorkflowEdge(source="response", target="continue_check"))

        # Loop back to intent detection
        edges.append(
            WorkflowEdge(
                source="continue_check",
                target="intent_detection",
                label="Yes",
                condition="User continues conversation",
            )
        )

        # 7. End Node
        end_node = WorkflowNode(
            id="end",
            type=NodeType.END,
            label="End",
            description="Conversation ends",
            position={"x": 100, "y": 650},
        )
        nodes.append(end_node)
        edges.append(
            WorkflowEdge(
                source="continue_check",
                target="end",
                label="No",
                condition="User ends conversation",
            )
        )

        return nodes, edges

    def _build_tool_nodes(self, tools: List[ToolConfigSchema]) -> List[WorkflowNode]:
        """Build nodes for each tool"""

        tool_nodes = []
        y_position = 350

        for i, tool in enumerate(tools):
            tool_node = WorkflowNode(
                id=f"tool_{i}_{tool.name.lower().replace(' ', '_')}",
                type=NodeType.TOOL_CALL,
                label=f"Call {tool.name}",
                description=tool.description or f"Use {tool.name} tool",
                config={
                    "tool_name": tool.name,
                    "endpoint": tool.endpoint,
                    "method": tool.method,
                    "input_schema": tool.input_schema,
                    "output_schema": tool.output_schema,
                    "usage_context": tool.usage_context,
                },
                position={"x": 300 + (i * 200), "y": y_position},
            )
            tool_nodes.append(tool_node)

        return tool_nodes

    def _generate_greeting(self, session_state: SessionState) -> str:
        """Generate greeting template"""

        tone_greetings = {
            "friendly": "Hi there! How can I help you today?",
            "professional": "Good day. How may I assist you?",
            "empathetic": "Hello! I'm here to help. What can I do for you?",
            "casual": "Hey! What's up? How can I help?",
            "formal": "Greetings. How may I be of assistance?",
        }

        # Try to match tone
        for key in tone_greetings:
            if key in (session_state.tone or "").lower():
                return tone_greetings[key]

        return f"Hello! I'm your {session_state.agent_type} assistant. How can I help you today?"

    def _extract_intents(self, session_state: SessionState) -> List[str]:
        """Extract expected intents from goals"""

        goals = session_state.goals or ""

        # Simple intent extraction based on keywords
        intents = []

        if "track" in goals.lower() or "status" in goals.lower():
            intents.append("check_status")

        if "return" in goals.lower() or "refund" in goals.lower():
            intents.append("process_return")

        if "book" in goals.lower() or "schedule" in goals.lower():
            intents.append("make_booking")

        if "cancel" in goals.lower():
            intents.append("cancel_request")

        if "help" in goals.lower() or "question" in goals.lower():
            intents.append("get_help")

        # Default intent
        if not intents:
            intents.append("general_inquiry")

        return intents

    def _generate_response_guidelines(self, session_state: SessionState) -> str:
        """Generate response guidelines"""

        guidelines = f"Always respond in a {session_state.tone} manner. "
        guidelines += f"Focus on: {session_state.goals}. "

        if session_state.use_tools:
            guidelines += "Use available tools to provide accurate information. "

        guidelines += "Be helpful, clear, and concise."

        return guidelines

    def _generate_workflow_description(self, session_state: SessionState) -> str:
        """Generate human-readable workflow description"""

        description = f"This is a {session_state.agent_type} voice agent "
        description += f"with a {session_state.tone} tone. "
        description += f"It is designed to {session_state.goals}. "

        if session_state.use_tools and session_state.tools:
            tool_names = ", ".join([tool.name for tool in session_state.tools])
            description += f"It uses the following tools: {tool_names}. "
        else:
            description += "It operates without external tool integrations. "

        return description


# Global instance
_synthesizer: Optional[WorkflowSynthesizer] = None


def get_synthesizer() -> WorkflowSynthesizer:
    """Get or create global synthesizer instance"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = WorkflowSynthesizer()
    return _synthesizer
