# AI Agent Builder Assistant - API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Session Management](#session-management)
  - [Workflow Management](#workflow-management)
  - [Prompt Generation](#prompt-generation)
- [Complete Usage Flow](#complete-usage-flow)
- [Code Examples](#code-examples)

---

## Overview

The AI Agent Builder Assistant is a conversational AI system that helps users create production-ready voice agents through natural dialogue. The system guides users through defining their agent's purpose, tone, and capabilities, then generates optimized system prompts and configurations for various platforms.

## Base URL

**Production:**
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online
```

**Local Development:**
```
http://localhost:8000
```

**API Version:** v1  
**API Base Path:** `/api/v1`

### Full Endpoint Format
```
https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1/{endpoint}
```

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Response Formats

All responses are in JSON format unless otherwise specified.

### Success Response
```json
{
  "session_id": "uuid",
  "status": "active",
  ...
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Internal Server Error | Server error |

---

## Endpoints

### Health Check

#### Check Server Health
```http
GET /health
```

**Description:** Check if the server is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T23:00:00Z"
}
```

**cURL Example:**
```bash
# Production
curl https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/health

# Local
curl http://localhost:8000/health
```

---

## Session Management

### 1. Create Session

#### Create a new agent building session
```http
POST /api/v1/sessions/create
```

**Description:** Creates a new session and returns the initial AI greeting.

**Request Body:**
```json
{
  "initial_message": "string (optional)"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "stage": "initial",
  "created_at": "2025-10-04T23:00:00Z",
  "message": "Hello! I'm here to help you design a voice agent..."
}
```

**cURL Example:**
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

**Python Example:**
```python
import requests

# Production
BASE_URL = "https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local
# BASE_URL = "http://localhost:8000/api/v1"

response = requests.post(
    f"{BASE_URL}/sessions/create",
    json={}
)
session = response.json()
session_id = session["session_id"]
print(f"Session created: {session_id}")
print(f"AI says: {session['message']}")
```

---

### 2. Send Message

#### Send a user message to the AI
```http
POST /api/v1/sessions/{session_id}/message
```

**Description:** Send a message to the AI and receive a response. The AI will ask questions to understand your agent requirements.

**Path Parameters:**
- `session_id` (string, required): The session ID from create session

**Request Body:**
```json
{
  "message": "I want to create a customer support agent"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "stage": "collecting_basics",
  "ai_response": "What specific tasks should this customer support agent handle?",
  "is_complete": false
}
```

**Conversation Stages:**
- `initial` - Starting the conversation
- `collecting_basics` - Deep dive into agent requirements (6-8+ detailed questions about:
  - Agent type and purpose
  - Detailed goals and behaviors
  - Tone and personality
  - Target users and use cases
  - Greeting style and conversation flow
  - Example interactions
  - Constraints and edge cases
  - Escalation rules and success criteria
  - Brand voice and verbosity level)
- `exploring_tools` - Asking about tool integrations
- `configuring_tools` - Setting up tool configurations
- `reviewing_workflow` - Comprehensive summary & confirmation (AI summarizes everything it understood, gets user confirmation, then shows workflow diagram)
- `finalizing` - Final confirmation and prompt generation
- `completed` - Session complete

**cURL Example:**
```bash
# Production
curl -X POST https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a customer support agent"}'
```

**Python Example:**
```python
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "I want a customer support agent"}
)
result = response.json()
print(f"Stage: {result['stage']}")
print(f"AI: {result['ai_response']}")
```

---

### 3. Get Session Status

#### Get current session information
```http
GET /api/v1/sessions/{session_id}/status
```

**Description:** Retrieve detailed information about the current session state.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "stage": "collecting_basics",
  "progress": 40,
  "collected_data": {
    "agent_type": "customer support",
    "goals": "Help customers with orders and returns",
    "tone": "friendly and professional",
    "use_tools": null,
    "tools": []
  },
  "conversation_length": 3,
  "created_at": "2025-10-04T23:00:00Z",
  "updated_at": "2025-10-04T23:05:00Z"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/status
```

---

### 4. Resume Session

#### Resume a previous session
```http
POST /api/v1/sessions/{session_id}/resume
```

**Description:** Resume a previously started session.

**Path Parameters:**
- `session_id` (string, required): The session ID to resume

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "stage": "exploring_tools",
  "message": "Welcome back! Let's continue building your agent..."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/resume
```

---

### 5. Delete Session

#### Delete a session
```http
DELETE /api/v1/sessions/{session_id}
```

**Description:** Delete a session and all its data.

**Path Parameters:**
- `session_id` (string, required): The session ID to delete

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

## Workflow Management

### 1. Get Workflow

#### Get the generated workflow
```http
GET /api/v1/workflows/{session_id}
```

**Description:** Retrieve the structured workflow for an agent.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_type": "customer_support",
    "goals": "Help customers with orders and returns",
    "tone": "friendly and professional",
    "use_tools": false,
    "tools": [],
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "label": "Start",
        "description": "Conversation begins"
      },
      {
        "id": "greeting",
        "type": "greeting",
        "label": "Greet User",
        "description": "Greet user with friendly and professional tone"
      }
    ],
    "edges": [
      {
        "source": "start",
        "target": "greeting"
      }
    ]
  },
  "mermaid_diagram": "flowchart TD\n    start[Start] --> greeting[Greet User]...",
  "is_final": false
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/workflows/550e8400-e29b-41d4-a716-446655440000
```

---

### 2. Visualize Workflow

#### Get workflow visualization
```http
GET /api/v1/workflows/{session_id}/visualize
```

**Description:** Get visual representations of the workflow.

**⚠️ When to Call:**
- **Stage: `reviewing_workflow`** - Call this endpoint when the conversation reaches the `reviewing_workflow` stage
- **AI includes workflow** - The AI's response will include the workflow summary in the message
- **Optional call** - You can call this endpoint to get the full Mermaid diagram and text summary for rendering
- **Frontend rendering** - Use this if you want to render the Mermaid diagram separately from the chat

**Note:** The workflow is automatically generated when entering `reviewing_workflow` stage. The AI's response includes a text summary, and you can optionally call this endpoint to get the full Mermaid diagram for visual rendering.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "mermaid_diagram": "flowchart TD\n    start[Start]\n    greeting[Greet User]\n    ...",
  "text_summary": "=== CUSTOMER_SUPPORT AGENT WORKFLOW ===\n\nDescription: ..."
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/workflows/550e8400-e29b-41d4-a716-446655440000/visualize
```

---

### 3. Review Workflow

#### Submit workflow feedback
```http
POST /api/v1/workflows/{session_id}/review
```

**Description:** Provide feedback on the workflow and request changes.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Request Body:**
```json
{
  "approved": true,
  "feedback": "Looks great!",
  "requested_changes": []
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved": true,
  "message": "Workflow approved! Proceeding to prompt generation..."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/550e8400-e29b-41d4-a716-446655440000/review \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "feedback": "Perfect!"}'
```

---

### 4. Regenerate Workflow

#### Regenerate workflow with changes
```http
POST /api/v1/workflows/{session_id}/regenerate
```

**Description:** Request workflow regeneration with specific changes.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Request Body:**
```json
{
  "changes": [
    "Add error handling step",
    "Include confirmation before actions"
  ]
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow": { ... },
  "mermaid_diagram": "...",
  "message": "Workflow regenerated with requested changes"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/550e8400-e29b-41d4-a716-446655440000/regenerate \
  -H "Content-Type: application/json" \
  -d '{"changes": ["Add error handling"]}'
```

---

## Prompt Generation

### 1. Generate Prompts

#### Generate system prompts in multiple formats
```http
POST /api/v1/prompts/{session_id}/generate
```

**Description:** Generate production-ready system prompts for various platforms.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Request Body:**
```json
{
  "formats": ["elevenlabs", "openai_assistant", "generic"]
}
```

**Available Formats:**
- `elevenlabs` - Voice-optimized for ElevenLabs
- `openai_assistant` - For OpenAI Assistant API
- `openai_chat` - For OpenAI Chat Completions
- `anthropic` - For Anthropic Claude
- `generic` - Universal format

**Response:**
```json
{
  "generic": {
    "format": "generic",
    "system_prompt": "You are a friendly and professional customer_support assistant...",
    "instructions": [
      "Primary goal: Help customers with orders and returns",
      "Maintain friendly and professional tone",
      "Ask clarifying questions when needed"
    ],
    "examples": null,
    "metadata": {
      "agent_type": "customer_support",
      "goals": "Help customers with orders and returns",
      "tone": "friendly and professional",
      "use_tools": false,
      "tool_count": 0,
      "generated_at": "2025-10-04T23:00:00Z"
    }
  },
  "elevenlabs": {
    "format": "elevenlabs",
    "system_prompt": "You are a friendly and professional customer_support voice agent...",
    ...
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/generate \
  -H "Content-Type: application/json" \
  -d '{"formats": ["elevenlabs", "openai_assistant"]}'
```

**Python Example:**
```python
response = requests.post(
    f"http://localhost:8000/api/v1/prompts/{session_id}/generate",
    json={"formats": ["elevenlabs", "openai_assistant", "generic"]}
)
prompts = response.json()

# Access specific format
elevenlabs_prompt = prompts["elevenlabs"]["system_prompt"]
print(f"ElevenLabs Prompt:\n{elevenlabs_prompt}")
```

---

### 2. Get Export Package

#### Get complete agent package
```http
GET /api/v1/prompts/{session_id}/export
```

**Description:** Get a complete export package including all prompts, tools, and workflow.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Query Parameters:**
- `include_workflow` (boolean, default: true): Include workflow diagram

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "customer_support",
  "agent_goals": "Help customers with orders and returns",
  "agent_tone": "friendly and professional",
  "prompts": {
    "generic": { ... },
    "elevenlabs": { ... },
    "openai_assistant": { ... },
    "openai_chat": { ... },
    "anthropic": { ... }
  },
  "tools": [],
  "workflow_diagram": "flowchart TD\n...",
  "workflow_summary": "=== CUSTOMER_SUPPORT AGENT WORKFLOW ===\n...",
  "created_at": "2025-10-04T23:00:00Z"
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/export?include_workflow=true"
```

---

### 3. Download Export

#### Download agent package as file
```http
GET /api/v1/prompts/{session_id}/export/download
```

**Description:** Download the complete agent package in a specific format. First download generates and stores in database, subsequent downloads retrieve from cache.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Query Parameters:**
- `format` (string, default: "json"): Export format
  - `json` - JSON format
  - `yaml` - YAML format
  - `markdown` - Markdown with diagrams
  - `text` - Plain text
- `include_workflow` (boolean, default: true): Include workflow

**Response:** File download with appropriate content-type header

**File Names:**
- JSON: `{agent_type}_agent.json`
- YAML: `{agent_type}_agent.yaml`
- Markdown: `{agent_type}_agent.md`
- Text: `{agent_type}_agent.txt`

**cURL Examples:**

Download JSON:
```bash
curl -O -J "http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/export/download?format=json"
```

Download YAML:
```bash
curl -O -J "http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/export/download?format=yaml"
```

Download Markdown:
```bash
curl -O -J "http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/export/download?format=markdown"
```

Download Text:
```bash
curl -O -J "http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/export/download?format=text"
```

**Python Example:**
```python
import requests

# Download JSON export
response = requests.get(
    f"http://localhost:8000/api/v1/prompts/{session_id}/export/download",
    params={"format": "json", "include_workflow": True}
)

# Save to file
with open("agent_export.json", "w") as f:
    f.write(response.text)

print("Export downloaded successfully!")
```

---

### 4. List Exports

#### List all exports for a session
```http
GET /api/v1/prompts/{session_id}/exports
```

**Description:** Get a list of all exports generated for this session (stored in database).

**Path Parameters:**
- `session_id` (string, required): The session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "exports": [
    {
      "id": "export-id-1",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_type": "customer_support",
      "format": "json",
      "file_size": "9784 bytes",
      "created_at": "2025-10-04T23:00:00Z"
    },
    {
      "id": "export-id-2",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_type": "customer_support",
      "format": "yaml",
      "file_size": "9736 bytes",
      "created_at": "2025-10-04T23:01:00Z"
    }
  ],
  "total": 2
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/prompts/550e8400-e29b-41d4-a716-446655440000/exports
```

---

## Complete Usage Flow

### Understanding the Conversation Flow

The AI Agent Builder uses a **comprehensive discovery process** to fully understand your requirements before generating outputs:

#### Flow Overview

1. **Initial** → Start conversation
2. **Collecting Basics** → 6-8+ detailed questions about:
   - What type of agent?
   - What specific tasks and behaviors?
   - What tone and personality?
   - Who are the target users?
   - How should it greet users?
   - What's the conversation flow?
   - Example interactions?
   - Any constraints or limitations?
   - Edge cases to handle?
   - Escalation rules?
   - Success criteria?
   - Brand voice and verbosity?
3. **Exploring Tools** → Need external integrations?
4. **Configuring Tools** → (If yes) Set up tool details
5. **Reviewing Workflow** → AI summarizes understanding, gets confirmation, shows diagram
6. **Finalizing** → Generate prompts
7. **Completed** → Download configuration

#### When to Call Which Endpoint

| Stage | Endpoint to Call | When | Purpose |
|-------|-----------------|------|---------|
| Initial | `POST /sessions/create` | On page load / new chat | Get session ID and first message |
| All stages | `POST /sessions/{id}/message` | Every user message | Continue conversation |
| Reviewing Workflow | `GET /workflows/{id}/visualize` | When `stage === "reviewing_workflow"` | Get Mermaid diagram for rendering (optional, workflow summary is in AI message) |
| Finalizing | `POST /prompts/{id}/generate` | When user approves workflow | Generate platform-specific prompts |
| Completed | `GET /prompts/{id}/export/download` | When ready to download | Download configuration file |

**Key Points:**
- The AI asks **many detailed questions** during `collecting_basics` - be patient!
- The workflow appears **after confirmation** in `reviewing_workflow` stage
- You **don't need** to call `/visualize` unless you want to render the Mermaid diagram
- The AI's message includes the workflow summary automatically

### Step-by-Step Example

Here's a complete workflow from creating a session to downloading the final agent configuration:

```python
import requests
import time

# Production
BASE_URL = "https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local Development
# BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Create Session
print("1. Creating session...")
response = requests.post(f"{BASE_URL}/sessions/create", json={})
session = response.json()
session_id = session["session_id"]
print(f"   Session ID: {session_id}")
print(f"   AI: {session['message']}\n")

# Step 2: Define Agent Type
print("2. Telling AI about agent type...")
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "I want to create a customer support agent"}
)
result = response.json()
print(f"   Stage: {result['stage']}")
print(f"   AI: {result['ai_response']}\n")

time.sleep(1)

# Step 3: Define Goals
print("3. Defining agent goals...")
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "Help customers with orders, returns, and general inquiries"}
)
result = response.json()
print(f"   Stage: {result['stage']}")
print(f"   AI: {result['ai_response']}\n")

time.sleep(1)

# Step 4: Define Tone
print("4. Defining agent tone...")
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "Professional but friendly and empathetic"}
)
result = response.json()
print(f"   Stage: {result['stage']}")
print(f"   AI: {result['ai_response']}\n")

time.sleep(1)

# Step 5: Tools Decision
print("5. Deciding on tools...")
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/message",
    json={"message": "No, I don't need external tools"}
)
result = response.json()
print(f"   Stage: {result['stage']}")
print(f"   AI: {result['ai_response'][:200]}...\n")

# Step 6: Get Workflow
print("6. Getting workflow...")
response = requests.get(f"{BASE_URL}/workflows/{session_id}")
workflow = response.json()
print(f"   Nodes: {len(workflow['workflow']['nodes'])}")
print(f"   Edges: {len(workflow['workflow']['edges'])}\n")

# Step 7: Visualize Workflow
print("7. Getting workflow visualization...")
response = requests.get(f"{BASE_URL}/workflows/{session_id}/visualize")
viz = response.json()
print(f"   Mermaid diagram: {len(viz['mermaid_diagram'])} characters")
print(f"   Text summary: {len(viz['text_summary'])} characters\n")

# Step 8: Generate Prompts
print("8. Generating prompts...")
response = requests.post(
    f"{BASE_URL}/prompts/{session_id}/generate",
    json={"formats": ["elevenlabs", "openai_assistant", "generic"]}
)
prompts = response.json()
print(f"   Generated {len(prompts)} prompt formats\n")

# Step 9: Get Complete Export
print("9. Getting complete export package...")
response = requests.get(f"{BASE_URL}/prompts/{session_id}/export")
export = response.json()
print(f"   Agent type: {export['agent_type']}")
print(f"   Prompt formats: {len(export['prompts'])}")
print(f"   Tools: {len(export['tools'])}\n")

# Step 10: Download as JSON
print("10. Downloading JSON export...")
response = requests.get(
    f"{BASE_URL}/prompts/{session_id}/export/download",
    params={"format": "json"}
)
with open("agent_export.json", "w") as f:
    f.write(response.text)
print("    Saved to: agent_export.json\n")

# Step 11: Download as Markdown
print("11. Downloading Markdown export...")
response = requests.get(
    f"{BASE_URL}/prompts/{session_id}/export/download",
    params={"format": "markdown"}
)
with open("agent_export.md", "w") as f:
    f.write(response.text)
print("    Saved to: agent_export.md\n")

# Step 12: List All Exports
print("12. Listing all exports...")
response = requests.get(f"{BASE_URL}/prompts/{session_id}/exports")
exports_list = response.json()
print(f"    Total exports in database: {exports_list['total']}")
for exp in exports_list['exports']:
    print(f"    - {exp['format']}: {exp['file_size']}")

print("\n✅ Complete workflow finished!")
print(f"Session ID: {session_id}")
```

---

## Code Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

// Production
const BASE_URL = 'https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1';

// Local Development
// const BASE_URL = 'http://localhost:8000/api/v1';

async function createAgent() {
  // Create session
  const sessionResp = await axios.post(`${BASE_URL}/sessions/create`, {});
  const sessionId = sessionResp.data.session_id;
  console.log(`Session created: ${sessionId}`);

  // Send message
  const messageResp = await axios.post(
    `${BASE_URL}/sessions/${sessionId}/message`,
    { message: 'I want a sales assistant' }
  );
  console.log(`AI Response: ${messageResp.data.ai_response}`);

  // Generate prompts
  const promptsResp = await axios.post(
    `${BASE_URL}/prompts/${sessionId}/generate`,
    { formats: ['elevenlabs', 'openai_assistant'] }
  );
  console.log('Prompts generated:', Object.keys(promptsResp.data));

  // Download export
  const exportResp = await axios.get(
    `${BASE_URL}/prompts/${sessionId}/export/download`,
    { params: { format: 'json' } }
  );
  
  // Save to file
  const fs = require('fs');
  fs.writeFileSync('agent_export.json', exportResp.data);
  console.log('Export saved!');
}

createAgent();
```

### cURL Script

```bash
#!/bin/bash

# Production
BASE_URL="https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/api/v1"

# Local Development
# BASE_URL="http://localhost:8000/api/v1"

# Create session
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions/create" -H "Content-Type: application/json" -d '{}')
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# Send message
curl -s -X POST "$BASE_URL/sessions/$SESSION_ID/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a customer support agent"}' | jq

# Generate prompts
curl -s -X POST "$BASE_URL/prompts/$SESSION_ID/generate" \
  -H "Content-Type: application/json" \
  -d '{"formats": ["elevenlabs", "generic"]}' | jq

# Download export
curl -O -J "$BASE_URL/prompts/$SESSION_ID/export/download?format=json"

echo "Done!"
```

---

## Quick Reference

### All Endpoints at a Glance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/sessions/create` | Create session |
| POST | `/api/v1/sessions/{id}/message` | Send message |
| GET | `/api/v1/sessions/{id}/status` | Get status |
| POST | `/api/v1/sessions/{id}/resume` | Resume session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |
| GET | `/api/v1/workflows/{id}` | Get workflow |
| GET | `/api/v1/workflows/{id}/visualize` | Visualize workflow |
| POST | `/api/v1/workflows/{id}/review` | Review workflow |
| POST | `/api/v1/workflows/{id}/regenerate` | Regenerate workflow |
| POST | `/api/v1/prompts/{id}/generate` | Generate prompts |
| GET | `/api/v1/prompts/{id}/export` | Get export package |
| GET | `/api/v1/prompts/{id}/export/download` | Download export |
| GET | `/api/v1/prompts/{id}/exports` | List exports |

---

## Support

For issues or questions:
- Check the logs at `/var/log/agent_builder.log`
- **Production API Docs**: `https://gent-uilder-carlisle-xiv448-pc4od78x.leapcell.online/docs`
- **Local API Docs**: `http://localhost:8000/docs`
- Check OpenAPI spec at `/openapi.json`

---

**Version:** 1.0.0  
**Last Updated:** October 4, 2025

