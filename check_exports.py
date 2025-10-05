"""
Check exports in database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.prompt.models import PromptExport

settings = get_settings()

# Create engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Query all exports
exports = db.query(PromptExport).all()

print(f"\n📊 Total Exports in Database: {len(exports)}\n")

for export in exports:
    print(f"ID: {export.id}")
    print(f"Session ID: {export.session_id}")
    print(f"Agent Type: {export.agent_type}")
    print(f"Format: {export.export_format.value}")
    print(f"File Size: {export.file_size}")
    print(f"Created: {export.created_at}")
    print(f"Content Preview: {export.content[:100]}...")
    print("-" * 70)

db.close()
