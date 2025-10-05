"""
Test script for Phase 3: Workflow Synthesizer
Tests the complete flow including workflow generation and visualization.
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"


def print_separator(title=""):
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print(f"{'=' * 70}\n")
    else:
        print(f"\n{'-' * 70}\n")


def test_complete_workflow():
    """Test complete conversation flow with workflow generation"""

    print_separator("🚀 PHASE 3: WORKFLOW SYNTHESIZER TEST")

    # Step 1: Create session
    print("1️⃣  Creating session...")
    response = requests.post(f"{BASE_URL}/api/v1/sessions/create", json={})
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session: {session_id}")
    print(f"🤖 AI: {session_data['message'][:100]}...")

    print_separator()

    # Step 2: Provide agent type
    print("2️⃣  User: I want a customer support agent")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "I want a customer support agent"},
    )
    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response'][:150]}...")

    sleep(1)
    print_separator()

    # Step 3: Provide goals
    print("3️⃣  User: Help customers track orders and process returns")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "Help customers track orders and process returns"},
    )
    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response'][:150]}...")

    sleep(1)
    print_separator()

    # Step 4: Provide tone
    print("4️⃣  User: Friendly and empathetic")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "Friendly and empathetic"},
    )
    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response'][:150]}...")

    sleep(1)
    print_separator()

    # Step 5: No tools (skip tool configuration)
    print("5️⃣  User: No, I don't need external tools")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "No, I don't need external tools"},
    )
    data = response.json()
    print(f"📊 Stage: {data['stage']}")

    # Check if we got workflow summary
    if len(data["ai_response"]) > 200:
        print(f"🤖 AI Response (first 200 chars):")
        print(data["ai_response"][:200] + "...")
        print("\n[Workflow summary generated!]")
    else:
        print(f"🤖 AI: {data['ai_response']}")

    print_separator()

    # Step 6: Get workflow via API
    print("6️⃣  Fetching workflow from API...")
    response = requests.get(f"{BASE_URL}/api/v1/workflows/{session_id}")

    if response.status_code == 200:
        workflow_data = response.json()
        print(f"✅ Workflow retrieved!")
        print(f"\nWorkflow Details:")
        print(f"  • Agent Type: {workflow_data['workflow']['agent_type']}")
        print(f"  • Goals: {workflow_data['workflow']['goals']}")
        print(f"  • Tone: {workflow_data['workflow']['tone']}")
        print(f"  • Uses Tools: {workflow_data['workflow']['use_tools']}")
        print(f"  • Nodes: {len(workflow_data['workflow']['nodes'])}")
        print(f"  • Edges: {len(workflow_data['workflow']['edges'])}")
        print(f"  • Is Final: {workflow_data['is_final']}")
    else:
        print(f"❌ Failed to get workflow: {response.status_code}")

    print_separator()

    # Step 7: Get workflow visualization
    print("7️⃣  Getting workflow visualization...")
    response = requests.get(f"{BASE_URL}/api/v1/workflows/{session_id}/visualize")

    if response.status_code == 200:
        viz_data = response.json()
        print("✅ Visualization retrieved!")
        print("\n📊 Mermaid Diagram:")
        print(viz_data["mermaid_diagram"])
        print("\n📝 Summary:")
        print(viz_data["summary"])
    else:
        print(f"❌ Failed to get visualization: {response.status_code}")

    print_separator()

    # Step 8: Check session status
    print("8️⃣  Final session status...")
    response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/status")
    status_data = response.json()

    print(f"\n📊 Session Summary:")
    print(f"   Stage: {status_data['stage']}")
    print(f"   Status: {status_data['status']}")
    print(f"   Progress: {status_data['progress_percentage']}%")
    print(f"\n   Collected Info:")
    for key, value in status_data["collected_info"].items():
        print(f"      • {key}: {value}")

    print_separator("✅ PHASE 3 TEST COMPLETE")
    print(f"Session ID: {session_id}")
    print("\nYou can now:")
    print(f"  • View workflow: GET {BASE_URL}/api/v1/workflows/{session_id}")
    print(f"  • Visualize: GET {BASE_URL}/api/v1/workflows/{session_id}/visualize")
    print(f"  • Review: POST {BASE_URL}/api/v1/workflows/{session_id}/review")
    print_separator()


def main():
    # Check health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
            test_complete_workflow()
        else:
            print(f"❌ Server returned {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running: python main.py")


if __name__ == "__main__":
    main()
