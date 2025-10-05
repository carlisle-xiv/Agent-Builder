# AI Agent Builder API

An AI-powered system that helps users design voice agents through intelligent conversation, automatically generating system prompts and tool configurations.

## 🎯 What We've Built So Far

### ✅ Session Management System
- **Session Creation**: Create unique sessions with automatic ID generation
- **Session Persistence**: 
  - Active state stored in Redis (fast access, TTL-based expiry)
  - Metadata stored in PostgreSQL/SQLite (permanent records)
- **Session Resumption**: Users can pause and continue sessions
- **Session Tracking**: Monitor progress, stage, and collected information

### ✅ Database & Storage
- **PostgreSQL/SQLite**: For persistent session records
- **Redis**: For active session state and conversation context
- **Alembic Migrations**: Database schema versioning

### ✅ API Endpoints
- `POST /api/v1/sessions/create` - Start a new agent building session
- `POST /api/v1/sessions/{session_id}/message` - Send user messages
- `GET /api/v1/sessions/{session_id}/status` - Get session progress
- `POST /api/v1/sessions/{session_id}/resume` - Resume a paused session
- `DELETE /api/v1/sessions/{session_id}` - Delete/abandon a session

### 📁 Project Structure
```
PROTOTYPE/
├── alembic/                    # Database migrations
│   └── versions/
├── src/
│   ├── session/               # Session feature module
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── router.py          # API endpoints
│   ├── app.py                 # FastAPI application
│   ├── config.py              # Settings management
│   ├── database.py            # Database connection
│   ├── redis_client.py        # Redis client
│   ├── models.py              # Central models import
│   ├── schemas.py             # Central schemas import
│   └── router.py              # Central router import
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## 🚀 Setup Instructions

### 1. Environment Variables
Create a `.env` file with your Redis credentials:

```env
# Database
DATABASE_URL=sqlite:///./agent_builder.db

# Redis
REDIS_HOST=your-redis-host.com
REDIS_PORT=15424
REDIS_DB=0
REDIS_USERNAME=default
REDIS_PASSWORD=your_redis_password

# LLM API Keys (add when ready)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Application
SESSION_EXPIRY_SECONDS=3600
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔄 Conversation Stages

The system guides users through these stages:
1. **INITIAL** - Session started
2. **COLLECTING_BASICS** - Gathering agent type, goals, tone
3. **EXPLORING_TOOLS** - Discussing tool needs
4. **CONFIGURING_TOOLS** - Setting up tool details
5. **REVIEWING_WORKFLOW** - User reviews the flow
6. **FINALIZING** - Generating final prompt
7. **COMPLETED** - Done

## 📝 Example Usage

### Create a Session
```bash
curl -X POST "http://localhost:8000/api/v1/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{"initial_message": "I want to build a customer support agent"}'
```

### Send a Message
```bash
curl -X POST "http://localhost:8000/api/v1/sessions/{session_id}/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want it to be friendly and professional"}'
```

### Check Status
```bash
curl -X GET "http://localhost:8000/api/v1/sessions/{session_id}/status"
```

## 🔨 Next Steps to Build

### 1. Conversation Orchestrator
- LLM-driven question generation
- Context-aware dialogue management
- Dynamic flow control

### 2. Intent Extractor
- Extract structured data from conversations
- Validate information completeness
- Update session state

### 3. Tool Selector
- Detect tool needs from conversation
- Propose relevant integrations
- Configure tool parameters

### 4. Workflow Synthesizer
- Compile collected data into structured flow
- Generate visual representations
- Allow user modifications

### 5. Prompt Generator
- Convert workflow to system prompt
- Generate tool configurations
- Format for target platforms (ElevenLabs, etc.)

## 🧪 Testing the Current System

Start the server and test the session management:
```bash
# Health check
curl http://localhost:8000/health

# Create a session
curl -X POST "http://localhost:8000/api/v1/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{}'

# Use the session_id from the response to test other endpoints
```

## 🛠️ Technology Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database
- **Alembic** - Database migrations
- **Redis** - Session state caching
- **Pydantic** - Data validation
- **OpenAI/Anthropic** - LLM integrations (coming next)

## 📖 Design Principles

1. **Modular Architecture**: Each feature has its own folder with models, schemas, and router
2. **Session Persistence**: Critical data in DB, active state in Redis
3. **RESTful API**: Clean, predictable endpoints
4. **Type Safety**: Pydantic schemas for all data
5. **Database Migrations**: Version-controlled schema changes

