# 🏗️ System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
│                    (Web, Mobile, CLI)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP/REST
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      FastAPI Server                          │
│                    (src/app.py)                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            API Router (src/router.py)              │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │     Session Router                           │  │    │
│  │  │     (src/session/router.py)                 │  │    │
│  │  │                                              │  │    │
│  │  │  • POST /sessions/create                    │  │    │
│  │  │  • POST /sessions/{id}/message              │  │    │
│  │  │  • GET  /sessions/{id}/status               │  │    │
│  │  │  • POST /sessions/{id}/resume               │  │    │
│  │  │  • DELETE /sessions/{id}                    │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                     │    │
│  │  [Future: Orchestrator, Tools, Workflow routers]   │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
               │                            │
         ┌─────▼────────┐           ┌──────▼──────┐
         │              │           │             │
         │   Redis      │           │  Database   │
         │   (Cache)    │           │  (SQLite/   │
         │              │           │  Postgres)  │
         └──────────────┘           └─────────────┘
         
    Active Session State         Persistent Records
    • conversation_history        • session metadata
    • collected_fields            • final_prompt
    • current_stage              • workflow_json
    • temporary_data             • tools_config
    • TTL: 1 hour                • permanent storage
```

## Data Flow

### 1. Create Session
```
Client                FastAPI              Database           Redis
  │                      │                    │                │
  ├──POST /create──────→ │                    │                │
  │                      ├──INSERT session──→ │                │
  │                      │ ←─session record──┤                │
  │                      │                    │                │
  │                      ├──SET session_state───────────────→ │
  │                      │ ←─OK──────────────────────────────┤
  │ ←─session_id + msg──┤                    │                │
  │                      │                    │                │
```

### 2. Send Message
```
Client                FastAPI              Database           Redis
  │                      │                    │                │
  ├─POST /message──────→ │                    │                │
  │                      ├──GET session_state─────────────────→│
  │                      │ ←─state───────────────────────────┤
  │                      │                    │                │
  │                      │  [Process message]                  │
  │                      │  [TODO: Call LLM]                   │
  │                      │  [TODO: Extract intent]             │
  │                      │  [TODO: Update stage]               │
  │                      │                    │                │
  │                      ├──UPDATE session──→ │                │
  │                      ├──SET new_state────────────────────→│
  │                      │                    │                │
  │ ←─AI response───────┤                    │                │
  │                      │                    │                │
```

### 3. Complete Session
```
Client                FastAPI              Database           Redis
  │                      │                    │                │
  │                      │  [Workflow complete]                │
  │                      │                    │                │
  │                      ├──UPDATE session──→ │                │
  │                      │  (status=completed)│                │
  │                      │  (final_prompt)    │                │
  │                      │  (workflow_json)   │                │
  │                      │  (tools_config)    │                │
  │                      │ ←─OK──────────────┤                │
  │                      │                    │                │
  │                      ├──DEL session_state─────────────────→│
  │ ←─final outputs─────┤                    │                │
  │                      │                    │                │
```

## Module Structure (Implemented)

```
src/
├── app.py                     # FastAPI application
├── config.py                  # Settings management (Pydantic)
├── database.py                # SQLAlchemy setup
├── redis_client.py            # Redis operations
├── models.py                  # Central model imports
├── schemas.py                 # Central schema imports
├── router.py                  # Central router imports
│
└── session/                   # Session feature module
    ├── __init__.py           # Feature exports
    ├── models.py             # Session database model
    │   └── Session           # SQLAlchemy model
    │   └── SessionStatus     # Enum (active/completed/abandoned)
    │
    ├── schemas.py            # Pydantic schemas
    │   ├── SessionCreate     # Request to create session
    │   ├── SessionResponse   # Session creation response
    │   ├── SessionState      # Full session state (Redis)
    │   ├── MessageRequest    # User message
    │   ├── MessageResponse   # AI response
    │   └── SessionStatusResponse  # Status details
    │
    └── router.py             # API endpoints
        ├── create_session()
        ├── send_message()
        ├── get_session_status()
        ├── resume_session()
        └── delete_session()
```

## Future Modules (To Be Built)

```
src/
├── llm/                       # LLM integration
│   ├── client.py             # OpenAI, Anthropic wrappers
│   ├── prompts.py            # Prompt templates
│   └── router.py             # LLM management endpoints
│
├── orchestrator/              # Conversation orchestration
│   ├── conversation.py       # Main orchestrator logic
│   ├── stages.py             # Stage management
│   ├── schemas.py            # Orchestrator schemas
│   └── router.py             # Orchestrator endpoints
│
├── intent/                    # Intent extraction
│   ├── extractor.py          # NLP extraction
│   ├── validators.py         # Data validation
│   └── schemas.py            # Intent schemas
│
├── tools/                     # Tool configuration
│   ├── selector.py           # Tool selection logic
│   ├── library.py            # Common tools catalog
│   ├── models.py             # Tool database models
│   ├── schemas.py            # Tool schemas
│   └── router.py             # Tool endpoints
│
├── workflow/                  # Workflow synthesis
│   ├── synthesizer.py        # Workflow builder
│   ├── visualizer.py         # Visual flow generator
│   ├── models.py             # Workflow models
│   ├── schemas.py            # Workflow schemas
│   └── router.py             # Workflow endpoints
│
└── prompt/                    # Prompt generation
    ├── generator.py          # System prompt generator
    ├── templates.py          # Prompt templates
    ├── formatters.py         # Platform formatters
    ├── schemas.py            # Prompt schemas
    └── router.py             # Prompt endpoints
```

## Database Schema (Current)

### sessions table
```sql
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    status VARCHAR CHECK(status IN ('active', 'completed', 'abandoned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    final_prompt TEXT NULL,
    workflow_json TEXT NULL,
    tools_config TEXT NULL
);

CREATE INDEX ix_sessions_id ON sessions(id);
```

## Redis Data Structure

### Session State (session:{session_id})
```json
{
  "session_id": "uuid",
  "stage": "initial",
  "agent_type": null,
  "goals": null,
  "tone": null,
  "use_tools": null,
  "tools": [],
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "message",
      "timestamp": "ISO8601"
    }
  ],
  "collected_fields": [],
  "workflow": null,
  "final_prompt": null,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**TTL:** 3600 seconds (1 hour, configurable)

## Configuration

### Environment Variables
```
DATABASE_URL          # Database connection string
REDIS_HOST            # Redis server host
REDIS_PORT            # Redis server port
REDIS_DB              # Redis database number
REDIS_USERNAME        # Redis username
REDIS_PASSWORD        # Redis password
OPENAI_API_KEY        # OpenAI API key (future)
ANTHROPIC_API_KEY     # Anthropic API key (future)
SESSION_EXPIRY_SECONDS # Session TTL in Redis
```

## API Documentation

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc  
**Health:** http://localhost:8000/health

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | Modern async API framework |
| **Database ORM** | SQLAlchemy | Database abstraction |
| **Migrations** | Alembic | Database version control |
| **Cache** | Redis | Session state storage |
| **Validation** | Pydantic | Data validation & schemas |
| **LLM (future)** | OpenAI, Anthropic | AI conversation |
| **Server** | Uvicorn | ASGI server |

## Design Patterns

1. **Feature-Based Modularity**
   - Each feature in own folder
   - Separate models, schemas, router per feature
   - Central imports for convenience

2. **Separation of Concerns**
   - Redis: Fast, ephemeral session state
   - Database: Permanent records
   - Router: API logic only
   - Models: Data structure only
   - Schemas: Validation & serialization

3. **Dependency Injection**
   - FastAPI's `Depends()` for DB sessions
   - Centralized config via `get_settings()`

4. **Type Safety**
   - Pydantic models for all data
   - Type hints throughout
   - Runtime validation

## Current Limitations (To Be Addressed)

1. ❌ No AI-powered responses yet (placeholder only)
2. ❌ No intent extraction from messages
3. ❌ No stage progression logic
4. ❌ No workflow synthesis
5. ❌ No final prompt generation
6. ❌ No tool configuration

**Next Phase: Build Conversation Orchestrator to address items 1-3**

## Scalability Considerations

- **Horizontal Scaling:** Stateless API (session in Redis)
- **Database Pooling:** SQLAlchemy connection pool
- **Caching:** Redis for all active sessions
- **Rate Limiting:** Can add per-user limits
- **Load Balancing:** Ready for multiple instances

---

**Status:** Phase 1 Complete ✅  
**Next:** Phase 2 - Conversation Orchestrator 🚀

