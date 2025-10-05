"""
Test script for Phase 4: Prompt Generator

Tests the complete flow:
1. Create session and build agent
2. Generate prompts in multiple formats
3. Export complete agent package
4. Download in different formats
"""

import requests
import time
import json
from typing import Dict, Any


API_BASE = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_subsection(title: str):
    """Print a formatted subsection"""
    print(f"\n{'-' * 70}")
    print(f"{title}")
    print(f"{'-' * 70}\n")


def test_prompt_generator():
    """Test the complete prompt generation flow"""

    print_section("🚀 PHASE 4: PROMPT GENERATOR TEST")

    # 1. Create session
    print("1️⃣  Creating session...")
    response = requests.post(f"{API_BASE}/sessions/create", json={})
    assert response.status_code == 201
    session_id = response.json()["session_id"]
    print(f"✅ Session: {session_id}")
    initial_message = response.json().get("message", "")
    if initial_message:
        print(f"🤖 AI: {initial_message[:100]}...\n")
    else:
        print("🤖 AI: (No initial message)\n")

    print_subsection("")

    # 2. Build the agent through conversation
    print("2️⃣  Building agent through conversation...")

    # Message 1: Agent type
    print("User: I want a sales assistant")
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/message",
        json={"message": "I want a sales assistant"},
    )
    assert response.status_code == 200
    print(f"📊 Stage: {response.json()['stage']}")
    ai_response = response.json()["ai_response"]
    print(f"🤖 AI: {ai_response[:150]}...\n")

    time.sleep(1)

    # Message 2: Goals
    print("User: Help customers find products and answer questions about pricing")
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/message",
        json={
            "message": "Help customers find products and answer questions about pricing"
        },
    )
    assert response.status_code == 200
    print(f"📊 Stage: {response.json()['stage']}")
    ai_response = response.json()["ai_response"]
    print(f"🤖 AI: {ai_response[:150]}...\n")

    time.sleep(1)

    # Message 3: Tone
    print("User: Professional but friendly")
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/message",
        json={"message": "Professional but friendly"},
    )
    assert response.status_code == 200
    print(f"📊 Stage: {response.json()['stage']}")
    ai_response = response.json()["ai_response"]
    print(f"🤖 AI: {ai_response[:150]}...\n")

    time.sleep(1)

    # Message 4: No tools
    print("User: No, I don't need external tools")
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/message",
        json={"message": "No, I don't need external tools"},
    )
    assert response.status_code == 200
    print(f"📊 Stage: {response.json()['stage']}")
    ai_response = response.json()["ai_response"]
    print(f"🤖 AI Response (first 200 chars):")
    print(f"{ai_response[:200]}...\n")

    print_subsection("")

    # 3. Generate prompts in multiple formats
    print("3️⃣  Generating prompts in multiple formats...")
    response = requests.post(
        f"{API_BASE}/prompts/{session_id}/generate",
        json={"formats": ["generic", "elevenlabs", "openai_assistant"]},
    )
    assert response.status_code == 200
    prompts = response.json()
    print(f"✅ Generated {len(prompts)} prompts!\n")

    # Show each prompt
    for format_name, prompt_data in prompts.items():
        print(f"📝 {format_name.upper()} Format:")
        print(f"   First 150 chars: {prompt_data['system_prompt'][:150]}...")
        print(f"   Instructions: {len(prompt_data['instructions'])}")
        print("")

    print_subsection("")

    # 4. Get complete export package
    print("4️⃣  Getting complete export package...")
    response = requests.get(
        f"{API_BASE}/prompts/{session_id}/export",
        params={"include_workflow": True},
    )
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
    export_package = response.json()
    print("✅ Export package created!\n")

    print("Package Contents:")
    print(f"  • Agent Type: {export_package['agent_type']}")
    print(f"  • Goals: {export_package['agent_goals']}")
    print(f"  • Tone: {export_package['agent_tone']}")
    print(f"  • Prompts: {len(export_package['prompts'])} formats")
    print(f"  • Tools: {len(export_package['tools'])}")
    print(f"  • Workflow: {'✅' if export_package['workflow_diagram'] else '❌'}")
    print("")

    print_subsection("")

    # 5. Test different export formats
    print("5️⃣  Testing export formats...")

    formats_to_test = ["json", "yaml", "markdown", "text"]

    for export_format in formats_to_test:
        print(f"\n📥 Downloading {export_format.upper()} format...")
        response = requests.get(
            f"{API_BASE}/prompts/{session_id}/export/download",
            params={"format": export_format, "include_workflow": True},
        )
        assert response.status_code == 200

        content = response.text
        content_preview = content[:200].replace("\n", " ")
        print(f"   Size: {len(content)} characters")
        print(f"   Preview: {content_preview}...")

        # Save to file for inspection
        filename = f"test_export_{session_id[:8]}.{export_format}"
        with open(filename, "w") as f:
            f.write(content)
        print(f"   ✅ Saved to: {filename}")

    print_subsection("")

    # 6. Show sample prompts
    print("6️⃣  Sample Generated Prompts...")

    # Show ElevenLabs prompt
    if "elevenlabs" in prompts:
        print("\n📢 ElevenLabs Prompt (Voice Agent):")
        print("─" * 70)
        elevenlabs_prompt = prompts["elevenlabs"]["system_prompt"]
        print(elevenlabs_prompt[:400])
        print("...")
        print("")

    # Show OpenAI Assistant prompt
    if "openai_assistant" in prompts:
        print("🤖 OpenAI Assistant Prompt:")
        print("─" * 70)
        openai_prompt = prompts["openai_assistant"]["system_prompt"]
        print(openai_prompt[:400])
        print("...")
        print("")

    print_subsection("")

    # 7. Verify workflow in export
    print("7️⃣  Verifying workflow in export...")
    if export_package.get("workflow_diagram"):
        diagram = export_package["workflow_diagram"]
        print("✅ Workflow diagram included")
        print(f"   Diagram size: {len(diagram)} characters")
        print(f"   Has 'flowchart': {'flowchart' in diagram}")
        print(f"   Has nodes: {diagram.count('[')}")
        print("")

        # Show first few lines
        print("   First few lines:")
        for line in diagram.split("\n")[:5]:
            print(f"     {line}")
        print("")

    if export_package.get("workflow_summary"):
        summary = export_package["workflow_summary"]
        print("✅ Workflow summary included")
        print(f"   Summary size: {len(summary)} characters")
        print("")

    print_subsection("")

    print_section("✅ PHASE 4 TEST COMPLETE")

    print(f"Session ID: {session_id}\n")
    print("You can now:")
    print(f"  • Generate prompts: POST {API_BASE}/prompts/{session_id}/generate")
    print(f"  • Get export: GET {API_BASE}/prompts/{session_id}/export")
    print(f"  • Download: GET {API_BASE}/prompts/{session_id}/export/download")
    print("")
    print("Export files created:")
    for fmt in formats_to_test:
        print(f"  - test_export_{session_id[:8]}.{fmt}")

    print(f"\n{'-' * 70}\n")


if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print("✅ Server is healthy\n")
        else:
            print("⚠️  Server health check failed")
            exit(1)
    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to server. Make sure it's running on http://localhost:8000"
        )
        exit(1)

    test_prompt_generator()
