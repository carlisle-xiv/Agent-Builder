"""
Quick script to verify PostgreSQL connection and tables
"""

from sqlalchemy import create_engine, inspect, text
from src.config import get_settings

settings = get_settings()

print(f"🔍 Connecting to: {settings.database_url.split('@')[1].split('/')[0]}...")
print(f"   Database: {settings.database_url.split('/')[-1].split('?')[0]}\n")

try:
    engine = create_engine(settings.database_url)

    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL!")
        print(f"   Version: {version[:50]}...\n")

    # Inspect tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"📊 Tables found: {len(tables)}")
    for table in tables:
        print(f"   • {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"      - {col['name']}: {col['type']}")

    print("\n✅ All tables created successfully in PostgreSQL!")

    # Check if we can query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sessions"))
        count = result.fetchone()[0]
        print(f"\n📈 Current sessions in database: {count}")

except Exception as e:
    print(f"❌ Error: {e}")
