"""
Workflow Visualizer - Creates visual representations of workflows.
"""

from src.workflow.schemas import WorkflowData, NodeType


# Mermaid reserved keywords that cannot be used as node IDs
MERMAID_RESERVED_KEYWORDS = {
    "end",
    "graph",
    "subgraph",
    "style",
    "class",
    "classDef",
    "click",
    "call",
    "direction",
    "TD",
    "TB",
    "BT",
    "RL",
    "LR",
}


def _sanitize_node_id(node_id: str) -> str:
    """Sanitize node ID to avoid Mermaid reserved keywords"""
    if node_id.lower() in MERMAID_RESERVED_KEYWORDS:
        return f"{node_id}Node"
    return node_id


def generate_mermaid_diagram(workflow: WorkflowData) -> str:
    """
    Generate a Mermaid.js flowchart diagram from workflow.

    Args:
        workflow: Workflow data

    Returns:
        Mermaid diagram string
    """

    lines = ["flowchart TD"]
    lines.append(f"    %% {workflow.agent_type} Agent Workflow")
    lines.append("")

    # Add nodes
    for node in workflow.nodes:
        node_shape = _get_node_shape(node.type)
        # Remove all quotes from label (not just replace with single quote)
        label = node.label.replace('"', "").replace("'", "")
        sanitized_id = _sanitize_node_id(node.id)
        lines.append(f"    {sanitized_id}{node_shape[0]}{label}{node_shape[1]}")

    lines.append("")

    # Add edges
    for edge in workflow.edges:
        source = _sanitize_node_id(edge.source)
        target = _sanitize_node_id(edge.target)
        if edge.label:
            label = edge.label.replace('"', "'")
            lines.append(f"    {source} -->|{label}| {target}")
        else:
            lines.append(f"    {source} --> {target}")

    # Add styling
    lines.append("")
    lines.append("    %% Styling")
    lines.append("    classDef startEnd fill:#90EE90,stroke:#333,stroke-width:2px")
    lines.append("    classDef tool fill:#FFE4B5,stroke:#333,stroke-width:2px")
    lines.append("    classDef condition fill:#87CEEB,stroke:#333,stroke-width:2px")
    lines.append("")

    # Sanitize node IDs in class assignments
    start_end_nodes = [
        _sanitize_node_id(n.id)
        for n in workflow.nodes
        if n.type in [NodeType.START, NodeType.END]
    ]
    if start_end_nodes:
        lines.append(f"    class {','.join(start_end_nodes)} startEnd")

    # Find tool nodes
    tool_nodes = [
        _sanitize_node_id(n.id) for n in workflow.nodes if n.type == NodeType.TOOL_CALL
    ]
    if tool_nodes:
        lines.append(f"    class {','.join(tool_nodes)} tool")

    # Find condition nodes
    condition_nodes = [
        _sanitize_node_id(n.id) for n in workflow.nodes if n.type == NodeType.CONDITION
    ]
    if condition_nodes:
        lines.append(f"    class {','.join(condition_nodes)} condition")

    return "\n".join(lines)


def _get_node_shape(node_type: NodeType) -> tuple[str, str]:
    """Get Mermaid shape brackets for node type"""

    shapes = {
        NodeType.START: ("[", "]"),  # Rectangle
        NodeType.END: ("[", "]"),  # Rectangle
        NodeType.GREETING: ("[", "]"),  # Rectangle
        NodeType.INTENT_DETECTION: ("[", "]"),  # Rectangle
        NodeType.TOOL_CALL: ("[", "]"),  # Rectangle
        NodeType.RESPONSE: ("[", "]"),  # Rectangle
        NodeType.CONDITION: ("{", "}"),  # Diamond
    }

    return shapes.get(node_type, ("[", "]"))


def generate_text_summary(workflow: WorkflowData) -> str:
    """
    Generate human-readable text summary of workflow.

    Args:
        workflow: Workflow data

    Returns:
        Text summary
    """

    summary = []
    summary.append(f"=== {workflow.agent_type.upper()} AGENT WORKFLOW ===\n")
    summary.append(f"Description: {workflow.description}\n")
    summary.append(f"Tone: {workflow.tone}")
    summary.append(f"Goals: {workflow.goals}\n")

    if workflow.use_tools and workflow.tools:
        summary.append(f"Tools ({len(workflow.tools)}):")
        for i, tool in enumerate(workflow.tools, 1):
            summary.append(f"  {i}. {tool.get('name', 'Unknown')}")
            if tool.get("description"):
                summary.append(f"     - {tool['description']}")
        summary.append("")

    summary.append("Workflow Steps:")
    summary.append(f"  Total Nodes: {len(workflow.nodes)}")
    summary.append(f"  Total Edges: {len(workflow.edges)}")
    summary.append("")

    # List key nodes
    summary.append("Key Steps:")
    for node in workflow.nodes:
        if node.type in [
            NodeType.GREETING,
            NodeType.INTENT_DETECTION,
            NodeType.TOOL_CALL,
            NodeType.RESPONSE,
        ]:
            summary.append(f"  → {node.label}: {node.description or 'N/A'}")

    return "\n".join(summary)
