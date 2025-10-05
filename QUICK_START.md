# Quick Start Guide

## 🌐 Production Deployment

**The API is live at:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online
```

**Try it now:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs
```

---

## Get Up and Running Locally in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/agent_builder
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Setup Database
```bash
alembic upgrade head
```

### 4. Start Server
```bash
python main.py
```

Server runs on: **http://localhost:8000**

---

## Test It Out

### Via Browser

**Production:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs
```

**Local:**
```
http://localhost:8000/docs
```

### Via cURL
```bash
# Production
curl -X POST https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{}'

# Local
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Via Python
```python
import requests

# Production
BASE_URL = "https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local
# BASE_URL = "http://localhost:8000/api/v1"

# Create session
response = requests.post(f"{BASE_URL}/sessions/create", json={})
session_id = response.json()["session_id"]
print(f"Session: {session_id}")
```

---

## Complete Example

```python
import requests

# Production
BASE = "https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local
# BASE = "http://localhost:8000/api/v1"

# 1. Create session
r = requests.post(f"{BASE}/sessions/create", json={})
sid = r.json()["session_id"]

# 2. Tell AI what you want
r = requests.post(f"{BASE}/sessions/{sid}/message",
    json={"message": "I want a customer support agent"})
print(r.json()["ai_response"])

# 3. Define goals
r = requests.post(f"{BASE}/sessions/{sid}/message",
    json={"message": "Help with orders and returns"})

# 4. Define tone
r = requests.post(f"{BASE}/sessions/{sid}/message",
    json={"message": "Professional but friendly"})

# 5. Tools
r = requests.post(f"{BASE}/sessions/{sid}/message",
    json={"message": "No external tools needed"})

# 6. Download agent config
r = requests.get(f"{BASE}/prompts/{sid}/export/download?format=json")
with open("my_agent.json", "w") as f:
    f.write(r.text)

print("✅ Agent created and saved to my_agent.json!")
```

---

## What's Available

### Prompt Formats
- `elevenlabs` - Voice agents
- `openai_assistant` - OpenAI Assistants
- `openai_chat` - Chat completions
- `anthropic` - Claude
- `generic` - Universal

### Export Formats
- `json` - Structured data
- `yaml` - Config files
- `markdown` - Documentation
- `text` - Plain text

---

## Next Steps

1. **Read Full API Docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Try Production API**: https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs
3. **Run Tests**: `python test_prompt_generator.py`
4. **Local Interactive Docs**: http://localhost:8000/docs
5. **Check Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Common Issues

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`

### Redis Connection Error
- Check Redis is running
- Verify REDIS_HOST and REDIS_PASSWORD

### API Key Errors
- Add OPENAI_API_KEY to `.env`
- Add ANTHROPIC_API_KEY to `.env`

---

**That's it! You're ready to build agents! 🚀**

