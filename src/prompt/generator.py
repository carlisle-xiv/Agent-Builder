"""
Prompt Generator - Creates production-ready system prompts from session data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import yaml

from src.prompt.schemas import (
    PromptFormat,
    PromptExportFormat,
    GeneratedPrompt,
    ToolConfiguration,
    PromptExport,
)
from src.prompt.templates import PROMPT_GENERATORS
from src.session.schemas import SessionState
from src.workflow.schemas import WorkflowData
from src.workflow.visualizer import generate_mermaid_diagram, generate_text_summary


class PromptGenerator:
    """
    Generates production-ready system prompts and tool configurations.
    """

    def generate_prompt(
        self, session_state: SessionState, format: PromptFormat
    ) -> GeneratedPrompt:
        """
        Generate a system prompt in the specified format.

        Args:
            session_state: Current session state with all collected data
            format: Target format for the prompt

        Returns:
            Generated prompt with metadata
        """

        # Get the appropriate generator
        generator_func = PROMPT_GENERATORS.get(
            format.value, PROMPT_GENERATORS["generic"]
        )

        # Generate the prompt
        system_prompt = generator_func(
            agent_type=session_state.agent_type or "assistant",
            goals=session_state.goals or "assist users",
            tone=session_state.tone or "helpful",
            use_tools=session_state.use_tools or False,
            tools=session_state.tools,
        )

        # Build instructions list
        instructions = self._build_instructions(session_state)

        # Generate examples if needed
        examples = self._generate_examples(session_state)

        # Build metadata
        metadata = {
            "agent_type": session_state.agent_type,
            "goals": session_state.goals,
            "tone": session_state.tone,
            "use_tools": session_state.use_tools,
            "tool_count": len(session_state.tools) if session_state.tools else 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return GeneratedPrompt(
            format=format,
            system_prompt=system_prompt,
            instructions=instructions,
            examples=examples,
            metadata=metadata,
        )

    def generate_all_prompts(
        self, session_state: SessionState, formats: List[PromptFormat] = None
    ) -> Dict[str, GeneratedPrompt]:
        """
        Generate prompts for multiple formats.

        Args:
            session_state: Current session state
            formats: List of formats to generate (default: all)

        Returns:
            Dictionary mapping format names to generated prompts
        """

        if formats is None:
            formats = list(PromptFormat)

        prompts = {}
        for format in formats:
            prompts[format.value] = self.generate_prompt(session_state, format)

        return prompts

    def generate_tool_configurations(
        self, session_state: SessionState
    ) -> List[ToolConfiguration]:
        """
        Generate tool configurations from session data.

        Args:
            session_state: Current session state

        Returns:
            List of tool configurations
        """

        if not session_state.use_tools or not session_state.tools:
            return []

        tool_configs = []
        for tool_data in session_state.tools:
            tool_config = ToolConfiguration(
                name=tool_data.get("name", "Unnamed Tool"),
                description=tool_data.get("description", ""),
                parameters=tool_data.get("parameters", {}),
                endpoint=tool_data.get("endpoint"),
                method=tool_data.get("method", "POST"),
                headers=tool_data.get("headers", {}),
                extraction_rules=tool_data.get("extraction_rules", {}),
            )
            tool_configs.append(tool_config)

        return tool_configs

    def create_export_package(
        self,
        session_state: SessionState,
        workflow: Optional[WorkflowData] = None,
        prompt_formats: List[PromptFormat] = None,
        include_workflow: bool = True,
    ) -> PromptExport:
        """
        Create complete export package for the agent.

        Args:
            session_state: Current session state
            workflow: Workflow data (optional)
            prompt_formats: Formats to include
            include_workflow: Whether to include workflow diagram

        Returns:
            Complete export package
        """

        # Generate prompts
        prompts = self.generate_all_prompts(session_state, prompt_formats)

        # Generate tool configurations
        tools = self.generate_tool_configurations(session_state)

        # Get workflow visualizations if available
        workflow_diagram = None
        workflow_summary = None
        if include_workflow and workflow:
            workflow_diagram = generate_mermaid_diagram(workflow)
            workflow_summary = generate_text_summary(workflow)

        return PromptExport(
            session_id=session_state.session_id,
            agent_type=session_state.agent_type or "assistant",
            agent_goals=session_state.goals or "assist users",
            agent_tone=session_state.tone or "helpful",
            prompts=prompts,
            tools=tools,
            workflow_diagram=workflow_diagram,
            workflow_summary=workflow_summary,
            created_at=datetime.utcnow().isoformat(),
        )

    def export_to_format(
        self, export_package: PromptExport, format: PromptExportFormat
    ) -> str:
        """
        Export the package to a specific file format.

        Args:
            export_package: Complete export package
            format: Output format

        Returns:
            Formatted string ready for file output
        """

        if format == PromptExportFormat.JSON:
            return json.dumps(
                export_package.model_dump(mode="json"), indent=2, ensure_ascii=False
            )

        elif format == PromptExportFormat.YAML:
            return yaml.dump(
                export_package.model_dump(mode="json"),
                default_flow_style=False,
                allow_unicode=True,
            )

        elif format == PromptExportFormat.MARKDOWN:
            return self._export_to_markdown(export_package)

        elif format == PromptExportFormat.TEXT:
            return self._export_to_text(export_package)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _build_instructions(self, session_state: SessionState) -> List[str]:
        """Build specific instructions list from session data"""

        instructions = []

        if session_state.goals:
            instructions.append(f"Primary goal: {session_state.goals}")

        if session_state.tone:
            instructions.append(f"Maintain {session_state.tone} tone")

        if session_state.use_tools:
            instructions.append("Use available tools when appropriate")

        instructions.extend(
            [
                "Ask clarifying questions when needed",
                "Provide clear, actionable responses",
                "Handle errors gracefully",
            ]
        )

        return instructions

    def _generate_examples(
        self, session_state: SessionState
    ) -> Optional[List[Dict[str, str]]]:
        """Generate example conversations based on agent type"""

        # For now, return None - can be extended later
        # to include actual example conversations
        return None

    def _export_to_markdown(self, export_package: PromptExport) -> str:
        """Export package as markdown document"""

        lines = []

        # Header
        lines.append(f"# {export_package.agent_type.upper()} Agent Configuration")
        lines.append(f"\n**Generated:** {export_package.created_at}")
        lines.append(f"**Session ID:** {export_package.session_id}\n")

        # Overview
        lines.append("## Overview")
        lines.append(f"- **Type:** {export_package.agent_type}")
        lines.append(f"- **Goals:** {export_package.agent_goals}")
        lines.append(f"- **Tone:** {export_package.agent_tone}")
        lines.append(f"- **Tools:** {len(export_package.tools)}\n")

        # System Prompts
        lines.append("## System Prompts")
        for format_name, prompt in export_package.prompts.items():
            lines.append(f"\n### {format_name.upper()}")
            lines.append("```")
            lines.append(prompt.system_prompt)
            lines.append("```\n")

        # Tools
        if export_package.tools:
            lines.append("## Tool Configurations")
            for tool in export_package.tools:
                lines.append(f"\n### {tool.name}")
                lines.append(f"**Description:** {tool.description}")
                if tool.endpoint:
                    lines.append(f"**Endpoint:** `{tool.method} {tool.endpoint}`")
                lines.append("")

        # Workflow
        if export_package.workflow_diagram:
            lines.append("## Workflow Diagram")
            lines.append("```mermaid")
            lines.append(export_package.workflow_diagram)
            lines.append("```\n")

        if export_package.workflow_summary:
            lines.append("## Workflow Summary")
            lines.append(export_package.workflow_summary)
            lines.append("")

        return "\n".join(lines)

    def _export_to_text(self, export_package: PromptExport) -> str:
        """Export package as plain text"""

        lines = []

        # Header
        lines.append("=" * 70)
        lines.append(f"  {export_package.agent_type.upper()} AGENT CONFIGURATION")
        lines.append("=" * 70)
        lines.append(f"Generated: {export_package.created_at}")
        lines.append(f"Session ID: {export_package.session_id}")
        lines.append("")

        # Overview
        lines.append("OVERVIEW")
        lines.append("-" * 70)
        lines.append(f"Type: {export_package.agent_type}")
        lines.append(f"Goals: {export_package.agent_goals}")
        lines.append(f"Tone: {export_package.agent_tone}")
        lines.append(f"Tools: {len(export_package.tools)}")
        lines.append("")

        # System Prompts
        lines.append("SYSTEM PROMPTS")
        lines.append("-" * 70)
        for format_name, prompt in export_package.prompts.items():
            lines.append(f"\n[ {format_name.upper()} ]")
            lines.append(prompt.system_prompt)
            lines.append("")

        # Tools
        if export_package.tools:
            lines.append("TOOL CONFIGURATIONS")
            lines.append("-" * 70)
            for i, tool in enumerate(export_package.tools, 1):
                lines.append(f"\n{i}. {tool.name}")
                lines.append(f"   Description: {tool.description}")
                if tool.endpoint:
                    lines.append(f"   Endpoint: {tool.method} {tool.endpoint}")
                lines.append("")

        # Workflow
        if export_package.workflow_summary:
            lines.append("WORKFLOW")
            lines.append("-" * 70)
            lines.append(export_package.workflow_summary)
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


# Global generator instance
_prompt_generator: Optional[PromptGenerator] = None


def get_prompt_generator() -> PromptGenerator:
    """Get or create the global prompt generator instance"""
    global _prompt_generator
    if _prompt_generator is None:
        _prompt_generator = PromptGenerator()
    return _prompt_generator
