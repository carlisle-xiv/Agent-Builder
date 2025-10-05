# 🚀 Quick Start Guide

## What We've Built

✅ **Session Management System** - Complete and working!
- Create sessions with unique IDs
- Store conversation state in Redis
- Track progress and metadata in database
- Resume sessions after pausing
- Full REST API

## Getting Started

### 1. Create Your `.env` File

```bash
# Copy and fill in your credentials
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./agent_builder.db

REDIS_HOST=redis-15424.c11.us-east-1-2.ec2.redns.redis-cloud.com
REDIS_PORT=15424
REDIS_DB=0
REDIS_USERNAME=default
REDIS_PASSWORD=EKUOKOL4DXsxL6upEpbhK2JZAaXX0HiC

OPENAI_API_KEY=
ANTHROPIC_API_KEY=

SESSION_EXPIRY_SECONDS=3600
EOF
```

### 2. Start the Server

```bash
python main.py
```

Server will be running at: **http://localhost:8000**

### 3. Test the API

#### Option A: Use the test script
```bash
# In a new terminal
python test_api.py
```

#### Option B: Use curl
```bash
# Health check
curl http://localhost:8000/health

# Create a session
curl -X POST "http://localhost:8000/api/v1/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{}'

# Send a message (replace SESSION_ID)
curl -X POST "http://localhost:8000/api/v1/sessions/SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to create a customer support agent"}'

# Check status
curl "http://localhost:8000/api/v1/sessions/SESSION_ID/status"
```

#### Option C: Use the interactive docs
Visit: **http://localhost:8000/docs**

## Project Structure

```
PROTOTYPE/
├── 📄 README.md          - Full documentation
├── 📄 PROGRESS.md        - Development progress & roadmap
├── 📄 ARCHITECTURE.md    - System architecture details
├── 📄 QUICKSTART.md      - This file
├── 📄 main.py            - Server entry point
├── 📄 test_api.py        - API test script
├── 📄 requirements.txt   - Python dependencies
├── 📄 .env               - Environment variables (YOU CREATE THIS)
├── 📄 alembic.ini        - Migration configuration
│
├── 📁 alembic/           - Database migrations
│   └── versions/         - Migration history
│
└── 📁 src/               - Source code
    ├── app.py           - FastAPI application
    ├── config.py        - Settings
    ├── database.py      - Database setup
    ├── redis_client.py  - Redis operations
    ├── models.py        - All models
    ├── schemas.py       - All schemas
    ├── router.py        - All routers
    │
    └── 📁 session/      - Session feature
        ├── models.py    - Session database model
        ├── schemas.py   - Session Pydantic schemas
        └── router.py    - Session API endpoints
```

## Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| POST | `/api/v1/sessions/create` | Create new session |
| POST | `/api/v1/sessions/{id}/message` | Send message |
| GET | `/api/v1/sessions/{id}/status` | Get session status |
| POST | `/api/v1/sessions/{id}/resume` | Resume session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

## Example Workflow

```python
import requests

BASE = "http://localhost:8000/api/v1"

# 1. Create session
resp = requests.post(f"{BASE}/sessions/create", json={})
session_id = resp.json()["session_id"]
print(f"AI: {resp.json()['message']}")

# 2. Send message
resp = requests.post(
    f"{BASE}/sessions/{session_id}/message",
    json={"message": "I want a customer support bot"}
)
print(f"AI: {resp.json()['ai_response']}")

# 3. Check status
resp = requests.get(f"{BASE}/sessions/{session_id}/status")
print(f"Progress: {resp.json()['progress_percentage']}%")
```

## What Works Now

✅ Session creation with unique IDs  
✅ Message storage in conversation history  
✅ Session state persistence (Redis + Database)  
✅ Progress tracking  
✅ Session resumption  
✅ Status monitoring  
✅ Full API documentation  

## What's Next

The placeholder response needs to be replaced with actual AI:

1. **Conversation Orchestrator** - AI asks intelligent questions
2. **Intent Extractor** - Understands what user wants
3. **Tool Selector** - Helps configure integrations
4. **Workflow Synthesizer** - Builds the flow
5. **Prompt Generator** - Creates final system prompt

## Documentation

- **API Docs:** http://localhost:8000/docs
- **Full README:** [README.md](README.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Progress:** [PROGRESS.md](PROGRESS.md)

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies
pip install -r requirements.txt
```

### Redis connection error
```bash
# Verify Redis credentials in .env
# Test Redis connection:
python -c "from src.redis_client import redis_client; print(redis_client.client.ping())"
```

### Database error
```bash
# Run migrations
alembic upgrade head

# Or delete and recreate
rm agent_builder.db
alembic upgrade head
```

## Development

### Add a new feature module

```bash
# Create feature folder
mkdir src/my_feature

# Create module files
touch src/my_feature/__init__.py
touch src/my_feature/models.py
touch src/my_feature/schemas.py
touch src/my_feature/router.py

# Import in central files
# - Add models to src/models.py
# - Add schemas to src/schemas.py
# - Add router to src/router.py
```

### Create a migration

```bash
# After changing models
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Testing

```bash
# Start server
python main.py

# In another terminal, run tests
python test_api.py

# Or use curl commands
curl http://localhost:8000/health
```

## Need Help?

1. Check [README.md](README.md) for detailed documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [PROGRESS.md](PROGRESS.md) for next steps
4. Visit http://localhost:8000/docs for interactive API docs

---

**🎉 Your session management system is ready!**

**Next step:** Build the Conversation Orchestrator to add AI-powered conversations.

See [PROGRESS.md](PROGRESS.md) for the complete roadmap.

