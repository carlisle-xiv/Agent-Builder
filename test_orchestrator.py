"""
Test script for the Conversation Orchestrator.
Run this to test the AI-powered conversation flow.
"""

import asyncio
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"


def print_separator():
    print("\n" + "=" * 70 + "\n")


async def test_full_conversation():
    """Test a complete conversation flow"""

    print_separator()
    print("🤖 CONVERSATION ORCHESTRATOR TEST")
    print_separator()

    # Step 1: Create session
    print("1️⃣  Creating new session...")
    response = requests.post(f"{BASE_URL}/api/v1/sessions/create", json={})

    if response.status_code != 201:
        print(f"❌ Failed to create session: {response.text}")
        return

    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session created: {session_id}")
    print(f"🤖 AI: {session_data['message']}")

    # Step 2: User describes agent type
    print_separator()
    print("2️⃣  User: I want to build a customer support agent")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "I want to build a customer support agent"},
    )

    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return

    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response']}")

    # Step 3: User provides goals
    print_separator()
    print("3️⃣  User: It should help customers track orders and handle returns")
    sleep(1)
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "It should help customers track orders and handle returns"},
    )

    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response']}")

    # Step 4: User provides tone
    print_separator()
    print("4️⃣  User: Friendly and empathetic")
    sleep(1)
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "Friendly and empathetic"},
    )

    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response']}")

    # Step 5: Tools question
    print_separator()
    print("5️⃣  User: Yes, I want to integrate with our order management API")
    sleep(1)
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "Yes, I want to integrate with our order management API"},
    )

    data = response.json()
    print(f"📊 Stage: {data['stage']}")
    print(f"🤖 AI: {data['ai_response']}")

    # Step 6: Check final status
    print_separator()
    print("6️⃣  Checking session status...")
    response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/status")
    status_data = response.json()

    print(f"\n📊 Final Session Status:")
    print(f"   Stage: {status_data['stage']}")
    print(f"   Progress: {status_data['progress_percentage']}%")
    print(f"   Collected Info:")
    for key, value in status_data["collected_info"].items():
        print(f"      • {key}: {value}")

    print_separator()
    print("✅ Test completed!")
    print(f"Session ID: {session_id}")
    print_separator()


def test_health():
    """Test server health"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running: python main.py")
        return False


def main():
    if not test_health():
        return

    # Run async test
    asyncio.run(test_full_conversation())


if __name__ == "__main__":
    main()
