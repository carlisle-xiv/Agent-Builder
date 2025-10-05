"""
Script to view sessions in PostgreSQL
"""

from sqlalchemy import create_engine, text
from src.config import get_settings
import json

settings = get_settings()
engine = create_engine(settings.database_url)

print("=" * 70)
print("📊 Sessions in PostgreSQL Database")
print("=" * 70)

try:
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT id, status, created_at, updated_at 
            FROM sessions 
            ORDER BY created_at DESC
        """)
        )

        sessions = result.fetchall()

        if not sessions:
            print("\n❌ No sessions found")
        else:
            print(f"\n✅ Found {len(sessions)} session(s):\n")

            for i, session in enumerate(sessions, 1):
                print(f"{i}. Session ID: {session[0]}")
                print(f"   Status: {session[1]}")
                print(f"   Created: {session[2]}")
                print(f"   Updated: {session[3]}")
                print()

        # Check Redis too
        print("-" * 70)
        print("🔍 Checking Redis for active session state...")

        from src.redis_client import redis_client

        for session in sessions:
            session_id = session[0]
            redis_data = redis_client.get_session(session_id)

            if redis_data:
                print(f"\n✅ Session {session_id[:8]}... found in Redis")
                print(f"   Stage: {redis_data.get('stage')}")
                print(
                    f"   Conversation history: {len(redis_data.get('conversation_history', []))} messages"
                )
            else:
                print(
                    f"\n⚠️  Session {session_id[:8]}... NOT in Redis (may have expired)"
                )

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
