# AI Agent Builder Assistant

> An intelligent conversational system that helps users create production-ready voice agents through natural dialogue.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Features

- **🤖 AI-Powered Conversation**: Natural dialogue to understand your agent requirements
- **🎯 Multi-LLM Support**: Intelligent routing between OpenAI GPT-4 and Anthropic Claude
- **📊 Workflow Generation**: Automatic workflow synthesis with visual diagrams
- **🎨 Multi-Platform Prompts**: Generate optimized prompts for ElevenLabs, OpenAI, Anthropic, and more
- **💾 Database Storage**: PostgreSQL for persistence, Redis for active sessions
- **📦 Export Formats**: JSON, YAML, Markdown, and plain text exports
- **🔄 Session Management**: Resume conversations anytime
- **✨ Zero Configuration**: Works out of the box with intelligent defaults

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd PROTOTYPE
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agent_builder

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_USERNAME=

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Start the server**
```bash
python main.py
```

The server will start on `http://localhost:8000` 🎉

**🌐 Live Production Deployment:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online
```

---

## 📖 Usage

### Option 1: Interactive API (Recommended)

Visit the interactive API documentation:

**Production:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs
```

**Local:**
```
http://localhost:8000/docs
```

### Option 2: cURL

```bash
# Production URL
BASE="https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Create a session
curl -X POST $BASE/sessions/create \
  -H "Content-Type: application/json" \
  -d '{}'

# Send a message
curl -X POST $BASE/sessions/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a customer support agent"}'

# Download the agent configuration
curl -O -J "$BASE/prompts/{session_id}/export/download?format=json"
```

### Option 3: Python

```python
import requests

# Production
BASE_URL = "https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local Development
# BASE_URL = "http://localhost:8000/api/v1"

# Create session
response = requests.post(f"{BASE_URL}/sessions/create", json={})
session_id = response.json()["session_id"]

# Have a conversation
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "I want a sales assistant"}
)
print(response.json()["ai_response"])

# Generate prompts
response = requests.post(
    f"{BASE_URL}/prompts/{session_id}/generate",
    json={"formats": ["elevenlabs", "openai_assistant"]}
)
prompts = response.json()
```

---

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference with examples
- **[Phase 1](PHASE1_COMPLETE.md)** - Session Management
- **[Phase 2](PHASE2_COMPLETE.md)** - Conversation Orchestrator
- **[Phase 3](PHASE3_COMPLETE.md)** - Workflow Synthesizer
- **[Phase 4](PHASE4_COMPLETE.md)** - Prompt Generator
- **[Database Exports](DATABASE_EXPORTS.md)** - Export storage system

---

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Redis │  │ PG DB│
└──────┘  └──────┘
```

### Tech Stack

- **Framework**: FastAPI
- **LLMs**: OpenAI GPT-4, Anthropic Claude 3.5 Sonnet
- **Databases**: PostgreSQL (persistence), Redis (sessions)
- **ORM**: SQLAlchemy with Alembic migrations
- **Validation**: Pydantic

### Project Structure

```
PROTOTYPE/
├── src/
│   ├── session/          # Session management
│   ├── orchestrator/     # Conversation orchestration
│   ├── workflow/         # Workflow synthesis
│   ├── prompt/           # Prompt generation
│   ├── llm/              # LLM integrations
│   └── app.py            # FastAPI application
├── alembic/              # Database migrations
├── tests/                # Test scripts
└── main.py               # Entry point
```

---

## 🎯 How It Works

### 1. **Comprehensive Discovery Phase**
The AI conducts a thorough interview (6-8+ questions) to deeply understand your needs:
- What type of agent do you want?
- What specific tasks and behaviors?
- What tone and personality?
- Who are your target users?
- How should it greet users?
- What's the expected conversation flow?
- Example interactions?
- Any constraints or limitations?
- Edge cases to handle?
- Escalation rules?
- Success criteria?
- Brand voice and verbosity preferences?
- Do you need tool integrations?

**Note:** This comprehensive approach ensures the final output matches your exact requirements

### 2. **Workflow Synthesis**
The system creates a structured workflow:
- Visual Mermaid diagram
- Node and edge definitions
- Text summary

### 3. **Prompt Generation**
Generate optimized prompts for multiple platforms:
- **ElevenLabs** - Voice-optimized prompts
- **OpenAI Assistant** - Structured with tool support
- **OpenAI Chat** - Chat completion format
- **Anthropic** - Claude-optimized with XML
- **Generic** - Universal format

### 4. **Export**
Download complete configuration:
- All prompt formats
- Workflow diagrams
- Tool configurations
- JSON, YAML, Markdown, or Text format

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test session management
python test_api.py

# Test conversation orchestrator
python test_orchestrator.py

# Test workflow synthesizer
python test_workflow.py

# Test prompt generator
python test_prompt_generator.py
```

Verify database:
```bash
# Check database structure
python verify_db.py

# Check session data
python check_sessions.py

# Check exports
python check_exports.py
```

---

## 🌐 API Endpoints

### Base URL

**Production:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1
```

**Local Development:**
```
http://localhost:8000/api/v1
```

### Sessions
- `POST /sessions/create` - Create new session
- `POST /sessions/{id}/message` - Send message
- `GET /sessions/{id}/status` - Get status
- `POST /sessions/{id}/resume` - Resume session
- `DELETE /sessions/{id}` - Delete session

### Workflows
- `GET /workflows/{id}` - Get workflow
- `GET /workflows/{id}/visualize` - Get visualization
- `POST /workflows/{id}/review` - Review workflow
- `POST /workflows/{id}/regenerate` - Regenerate

### Prompts
- `POST /prompts/{id}/generate` - Generate prompts
- `GET /prompts/{id}/export` - Get export package
- `GET /prompts/{id}/export/download` - Download file
- `GET /prompts/{id}/exports` - List all exports

See **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** for detailed documentation with examples.

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | Required |
| `REDIS_USERNAME` | Redis username | `` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |

### Database Setup

The system uses PostgreSQL with the following tables:
- `sessions` - Session metadata
- `workflows` - Generated workflows
- `prompt_exports` - Exported configurations

Migrations are managed with Alembic:
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📈 Performance

- **Session creation**: < 100ms
- **Message processing**: 2-5s (depending on LLM)
- **Workflow generation**: < 500ms
- **Prompt generation**: < 200ms
- **Export download**: < 100ms (cached)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- FastAPI for the excellent framework
- The open-source community

---

## 📞 Support

- **Documentation**: See `API_DOCUMENTATION.md`
- **Issues**: Open an issue on GitHub
- **Production API Docs**: `https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs`
- **Local API Docs**: `http://localhost:8000/docs`

---

**Built with ❤️ using FastAPI, OpenAI, and Anthropic Claude**

