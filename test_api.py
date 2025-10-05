"""
Quick test script to verify the API is working.
Run this after starting the server with: python main.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_create_session():
    """Test session creation"""
    print("🔍 Testing session creation...")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/create",
        json={"initial_message": "I want to build a customer support agent"},
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}\n")

    if response.status_code == 201:
        return data.get("session_id")
    return None


def test_send_message(session_id):
    """Test sending a message"""
    print(f"🔍 Testing send message for session {session_id}...")
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/message",
        json={"message": "I want it to be friendly and helpful"},
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_get_status(session_id):
    """Test getting session status"""
    print(f"🔍 Testing get status for session {session_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def test_resume_session(session_id):
    """Test resuming a session"""
    print(f"🔍 Testing resume for session {session_id}...")
    response = requests.post(f"{BASE_URL}/api/v1/sessions/{session_id}/resume")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200


def main():
    print("=" * 60)
    print("🚀 AI Agent Builder API Test Suite")
    print("=" * 60)
    print()

    try:
        # Test health
        if not test_health():
            print("❌ Health check failed. Is the server running?")
            return

        print("✅ Health check passed!\n")

        # Create session
        session_id = test_create_session()
        if not session_id:
            print("❌ Session creation failed")
            return

        print(f"✅ Session created: {session_id}\n")

        # Send message
        if not test_send_message(session_id):
            print("❌ Send message failed")
            return

        print("✅ Message sent successfully!\n")

        # Get status
        if not test_get_status(session_id):
            print("❌ Get status failed")
            return

        print("✅ Status retrieved successfully!\n")

        # Resume session
        if not test_resume_session(session_id):
            print("❌ Resume session failed")
            return

        print("✅ Session resumed successfully!\n")

        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
