"""
LLM Client supporting both OpenAI and Anthropic Claude.
Includes intelligent routing based on task type.
"""

import json
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from src.config import get_settings
from src.llm.schemas import LLMResponse, ExtractedData, ConfidenceScores
from src.session.schemas import ConversationStage

settings = get_settings()


class LLMProvider(str, Enum):
    """Available LLM providers"""

    OPENAI = "openai"
    CLAUDE = "claude"


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    Routes requests intelligently based on task type.
    """

    def __init__(self):
        # Initialize clients
        self.openai_client = (
            AsyncOpenAI(api_key=settings.openai_api_key)
            if settings.openai_api_key
            else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=settings.anthropic_api_key)
            if settings.anthropic_api_key
            else None
        )

        # Default models
        self.openai_model = "gpt-5"  # Latest GPT-5
        self.claude_model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet

    def _route_provider(self, stage: ConversationStage) -> LLMProvider:
        """
        Intelligently route to best provider based on stage.

        Claude: Better at empathetic conversation, exploration
        GPT-4: Better at structured extraction, precise tasks

        Args:
            stage: Current conversation stage

        Returns:
            Preferred LLM provider for this stage
        """
        # Claude for conversational, exploratory stages
        conversational_stages = [
            ConversationStage.INITIAL,
            ConversationStage.EXPLORING_TOOLS,
            ConversationStage.REVIEWING_WORKFLOW,
        ]

        # GPT-4 for structured extraction, configuration
        structured_stages = [
            ConversationStage.COLLECTING_BASICS,
            ConversationStage.CONFIGURING_TOOLS,
            ConversationStage.FINALIZING,
        ]

        if stage in conversational_stages and self.anthropic_client:
            return LLMProvider.CLAUDE
        elif stage in structured_stages and self.openai_client:
            return LLMProvider.OPENAI
        else:
            # Fallback to whatever is available
            if self.openai_client:
                return LLMProvider.OPENAI
            elif self.anthropic_client:
                return LLMProvider.CLAUDE
            else:
                raise ValueError("No LLM provider configured. Add API keys to .env")

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        stage: ConversationStage,
        provider: Optional[LLMProvider] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Send a message to LLM and get structured response.

        Args:
            system_prompt: System prompt for this stage
            user_message: Latest user message
            conversation_history: Previous conversation
            stage: Current conversation stage
            provider: Force specific provider (optional)
            temperature: LLM temperature (0.0-1.0)

        Returns:
            Structured LLM response
        """
        # Route to best provider
        if provider is None:
            provider = self._route_provider(stage)

        print(f"🤖 Routing to {provider.value} for stage {stage.value}")

        # Call appropriate provider
        if provider == LLMProvider.OPENAI:
            return await self._call_openai(
                system_prompt, user_message, conversation_history, temperature
            )
        elif provider == LLMProvider.CLAUDE:
            return await self._call_claude(
                system_prompt, user_message, conversation_history, temperature
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openai(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        temperature: float,
    ) -> LLMResponse:
        """Call OpenAI API with structured output"""

        if not self.openai_client:
            raise ValueError("OpenAI client not configured")

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 10 messages for context window)
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI with JSON mode
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            parsed = json.loads(content)

            # Convert to LLMResponse
            return self._parse_llm_response(parsed)

        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            # Return fallback response
            return self._fallback_response(
                "I apologize, but I encountered an error. Could you please rephrase that?"
            )

    async def _call_claude(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        temperature: float,
    ) -> LLMResponse:
        """Call Anthropic Claude API"""

        if not self.anthropic_client:
            raise ValueError("Anthropic client not configured")

        # Enhance system prompt with strict JSON requirements
        enhanced_system_prompt = f"""{system_prompt}

CRITICAL: You MUST respond with valid JSON only. No markdown, no explanations outside JSON.

Required JSON structure:
{{
    "next_question": "string - REQUIRED, never null",
    "extracted_data": {{}},
    "confidence": {{}},
    "needs_clarification": false,
    "clarification_question": null,
    "stage_complete": false,
    "reasoning": "string - explain your thinking"
}}

Rules:
- next_question MUST always be a non-empty string
- If you have nothing to ask, use "Is there anything else you'd like to add?"
- Never use null for next_question
- Always provide reasoning field"""

        # Build messages for Claude
        messages = []

        # Add conversation history
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call Claude
            response = await self.anthropic_client.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                temperature=temperature,
                system=enhanced_system_prompt,
                messages=messages,
            )

            # Extract content
            content = response.content[0].text

            # Try to parse as JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # Claude might not always return pure JSON
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                    parsed = json.loads(json_str)
                elif "```" in content:
                    # Try without json marker
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                    parsed = json.loads(json_str)
                else:
                    # Fallback: create structured response from text
                    print(f"⚠️  Claude returned non-JSON: {content[:200]}")
                    return LLMResponse(
                        next_question=content
                        if len(content) < 500
                        else "Could you tell me more about that?",
                        extracted_data=ExtractedData(),
                        confidence=ConfidenceScores(),
                        needs_clarification=False,
                        stage_complete=False,
                        reasoning="Direct text response from Claude",
                    )

            # Sanitize the parsed response before creating LLMResponse
            parsed = self._sanitize_claude_response(parsed)
            return self._parse_llm_response(parsed)

        except Exception as e:
            print(f"❌ Claude error: {e}")
            return self._fallback_response(
                "I apologize, but I encountered an error. Could you please rephrase that?"
            )

    def _sanitize_claude_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize Claude response to ensure required fields are present.

        Args:
            data: Raw response from Claude

        Returns:
            Sanitized response with all required fields
        """
        # Ensure next_question is always a string
        if not data.get("next_question") or data.get("next_question") is None:
            data["next_question"] = "Could you tell me more about that?"

        # Ensure extracted_data exists
        if "extracted_data" not in data:
            data["extracted_data"] = {}

        # Ensure confidence exists
        if "confidence" not in data:
            data["confidence"] = {}

        # Ensure boolean fields have defaults
        if "needs_clarification" not in data:
            data["needs_clarification"] = False

        if "stage_complete" not in data:
            data["stage_complete"] = False

        # Ensure reasoning exists
        if "reasoning" not in data:
            data["reasoning"] = "Processing user input"

        return data

    def _parse_llm_response(self, data: Dict[str, Any]) -> LLMResponse:
        """Parse LLM response into structured format"""

        try:
            # Ensure next_question is never None
            next_question = data.get("next_question")
            if not next_question:
                next_question = "Could you tell me more about that?"

            return LLMResponse(
                next_question=next_question,
                extracted_data=ExtractedData(**data.get("extracted_data", {})),
                confidence=ConfidenceScores(**data.get("confidence", {})),
                needs_clarification=data.get("needs_clarification", False),
                clarification_question=data.get("clarification_question"),
                stage_complete=data.get("stage_complete", False),
                reasoning=data.get("reasoning", ""),
            )
        except Exception as e:
            print(f"⚠️  Error parsing LLM response: {e}")
            print(f"📄 Raw data: {json.dumps(data, indent=2)}")
            # Return with minimal valid data
            return LLMResponse(
                next_question="Could you provide more details?",
                extracted_data=ExtractedData(),
                confidence=ConfidenceScores(),
                reasoning=f"Fallback due to parsing error: {str(e)}",
            )

    def _fallback_response(self, question: str) -> LLMResponse:
        """Generate fallback response when LLM fails"""
        return LLMResponse(
            next_question=question,
            extracted_data=ExtractedData(),
            confidence=ConfidenceScores(),
            needs_clarification=True,
            reasoning="Fallback due to LLM error",
        )


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create global LLM client instance.

    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
