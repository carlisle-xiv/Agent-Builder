# Frontend Generation Prompt for AI Agent Builder

## Project Overview
Build a modern, ChatGPT-style conversational interface for an AI Agent Builder Assistant. The application guides users through creating voice agents via natural dialogue and allows them to download the final configuration.

---

## Design Requirements

### Overall Style
- **ChatGPT-like interface**: Clean, modern, conversational UI
- **Color scheme**: Professional with accent colors for AI responses
- **Typography**: Clear, readable fonts (Inter or similar)
- **Responsive**: Works on desktop and mobile
- **Dark mode support**: Toggle between light and dark themes

### Layout Structure
```
┌─────────────────────────────────────────┐
│  Header: "AI Agent Builder"       [🌙]  │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 💬 AI Message                      │ │
│  │ Hello! I'm here to help you...    │ │
│  └────────────────────────────────────┘ │
│                                          │
│              ┌──────────────────────┐    │
│              │ 👤 User Message      │    │
│              │ I want a sales agent │    │
│              └──────────────────────┘    │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 💬 AI Message                      │ │
│  │ Great! What should it do?          │ │
│  └────────────────────────────────────┘ │
│                                          │
│              [Workflow Preview Here]     │
│              [Download Buttons Here]     │
│                                          │
├─────────────────────────────────────────┤
│ [  Type your message...          ] [→]  │
└─────────────────────────────────────────┘
```

---

## Core Features

### 1. Chat Interface
- **Message bubbles**: 
  - AI messages: Left-aligned, light background (blue/gray tint)
  - User messages: Right-aligned, darker background (purple/blue)
- **Auto-scroll**: Automatically scroll to latest message
- **Typing indicator**: Show "..." while AI is thinking
- **Timestamps**: Show time for each message (optional, on hover)
- **Message history**: All messages stay visible as conversation progresses

### 2. Input Area
- **Text input**: 
  - Multi-line support (grows with content, max 5 lines)
  - Placeholder: "Type your message..."
  - Submit on Enter (Shift+Enter for new line)
- **Send button**: 
  - Arrow icon (→) or paper plane icon
  - Disabled when input is empty
  - Shows loading state during API call
- **Character counter**: Optional, for very long inputs

### 3. Conversation Stages (Visual Indicators)
Show progress through stages at the top:
```
[●●●○○○] 
Initial → Basics → Tools → Workflow → Complete
```

Visual progress indicators:
- ✅ Completed stages (green)
- 🔵 Current stage (blue, pulsing)
- ⚪ Pending stages (gray)

Stage names:
1. Getting Started
2. Defining Agent
3. Tools & Integrations
4. Reviewing Workflow
5. Download Prompts

### 4. Workflow Preview
When the AI shows the workflow (Stage 4):
- **Collapsible section** titled "📊 Your Agent Workflow"
- **Mermaid diagram** rendered visually (use mermaid.js)
- **Text summary** below the diagram
- **Edit button** (optional): "Request Changes"

### 5. Download Section
When agent is complete:
- **Format selection**: Radio buttons or toggle
  ```
  Select Format:
  ○ ElevenLabs (Voice)
  ○ OpenAI Assistant
  ○ OpenAI Chat
  ○ Anthropic Claude
  ○ Generic (Universal)
  ```

- **Export format**: Dropdown
  ```
  Export as: [JSON ▼]
  Options: JSON, YAML, Markdown, Text
  ```

- **Download button**: 
  ```
  [⬇ Download Agent Configuration]
  ```
  Large, prominent button

- **Preview option**: "👁 Preview Configuration" (shows in modal)

### 6. Additional UI Elements

#### Header
- **Logo/Title**: "AI Agent Builder" with icon
- **New Chat button**: Start fresh conversation
- **Settings icon**: Access preferences
- **Dark mode toggle**: 🌙/☀️

#### Sidebar (Optional, can be hidden)
- **Chat history**: List of previous sessions
- **Example prompts**: Quick start templates
  - "Customer Support Agent"
  - "Sales Assistant"
  - "Technical Support Bot"
  - "Booking Assistant"

#### Empty State (First Load)
```
┌─────────────────────────────────────┐
│                                     │
│         🤖                          │
│   AI Agent Builder                  │
│                                     │
│   Let's create your perfect         │
│   voice agent together!             │
│                                     │
│   Example prompts:                  │
│   • "I want a customer support..."  │
│   • "Create a sales assistant..."   │
│   • "Help me build a booking..."    │
│                                     │
└─────────────────────────────────────┘
```

---

## Technical Implementation

### API Integration

**Base URL**: `http://localhost:8000/api/v1`

#### Flow:

1. **On page load / New Chat**:
   ```javascript
   POST /sessions/create
   Response: { session_id, message }
   → Display AI's initial message
   ```

2. **User sends message**:
   ```javascript
   POST /sessions/{session_id}/message
   Body: { message: "user input" }
   Response: { ai_response, stage, is_complete }
   → Add user message to chat
   → Show typing indicator
   → Add AI response to chat
   → Update progress indicator
   ```

3. **Check for workflow stage**:
   ```javascript
   If stage === "reviewing_workflow":
     GET /workflows/{session_id}/visualize
     Response: { mermaid_diagram, text_summary }
     → Render Mermaid diagram
     → Show workflow section
   ```

4. **When complete**:
   ```javascript
   If is_complete === true:
     → Show format selection UI
     → Show download button
   
   On format selection + download:
     POST /prompts/{session_id}/generate
     Body: { formats: [selected_format] }
     
     Then:
     GET /prompts/{session_id}/export/download?format=json
     → Trigger file download
   ```

#### Error Handling
- Network errors: Show retry button
- API errors: Display error message in chat
- Timeout: "Taking longer than expected..." message

---

## State Management

### Application State
```typescript
interface AppState {
  sessionId: string | null;
  messages: Message[];
  currentStage: Stage;
  isLoading: boolean;
  workflowData: WorkflowData | null;
  selectedFormat: PromptFormat;
  exportFormat: ExportFormat;
  isComplete: boolean;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

type Stage = 
  | 'initial' 
  | 'collecting_basics' 
  | 'exploring_tools' 
  | 'configuring_tools'
  | 'reviewing_workflow' 
  | 'finalizing' 
  | 'completed';

type PromptFormat = 
  | 'elevenlabs' 
  | 'openai_assistant' 
  | 'openai_chat' 
  | 'anthropic' 
  | 'generic';

type ExportFormat = 'json' | 'yaml' | 'markdown' | 'text';
```

---

## User Interaction Flow

### Happy Path

1. **User arrives at page**
   - Sees welcome message and empty chat
   - Reads initial AI greeting
   - Types first message: "I want a customer support agent"

2. **AI asks about goals**
   - User responds: "Help customers with orders and returns"
   - Progress bar shows stage 2/5

3. **AI asks about tone**
   - User responds: "Professional but friendly"
   - Progress bar advances

4. **AI asks about tools**
   - User responds: "No, I don't need external tools"
   - Progress bar advances

5. **AI shows workflow**
   - Mermaid diagram appears in chat
   - Collapsible workflow preview section
   - AI asks: "Does this look good?"

6. **User approves**
   - User responds: "Yes, looks perfect!"
   - Download section appears

7. **User selects format and downloads**
   - Selects "ElevenLabs (Voice)" format
   - Selects "JSON" export format
   - Clicks download button
   - File downloads: `customer_support_agent.json`
   - Success message appears

---

## Animations & Transitions

- **Message appearance**: Fade in + slide up (200ms)
- **Typing indicator**: Animated dots (3 dots bouncing)
- **Stage progress**: Smooth color transitions (300ms)
- **Workflow section**: Expand/collapse animation (400ms)
- **Button hover**: Scale slightly (1.05x)
- **Download button**: Pulse effect when ready

---

## Responsive Behavior

### Desktop (> 768px)
- Two-column layout (optional sidebar + chat)
- Max width: 1200px, centered
- Message bubbles: Max 70% width

### Tablet (768px - 1024px)
- Single column
- Collapsible sidebar
- Message bubbles: Max 80% width

### Mobile (< 768px)
- Full-width layout
- Hamburger menu for sidebar
- Message bubbles: Max 85% width
- Stack format/export selections vertically

---

## Accessibility

- **Keyboard navigation**: Tab through all interactive elements
- **Screen readers**: Proper ARIA labels
- **High contrast**: Ensure readable text contrast ratios
- **Focus indicators**: Clear focus states on all interactive elements
- **Alt text**: All icons have descriptive labels

---

## Suggested Tech Stack

### Recommended
- **Framework**: React with TypeScript or Next.js
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios or Fetch API
- **Diagram Rendering**: mermaid.js
- **Icons**: Lucide React or Heroicons
- **State**: React Context or Zustand

### Alternative
- **Framework**: Vue 3 with TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Diagram**: mermaid.js
- **Icons**: Heroicons Vue

---

## Color Palette Suggestion

### Light Mode
- Background: `#FFFFFF`
- Chat background: `#F7F9FC`
- AI message bubble: `#E8F0FE` (light blue)
- User message bubble: `#7C3AED` (purple)
- Text: `#1F2937` (dark gray)
- Accent: `#3B82F6` (blue)
- Success: `#10B981` (green)

### Dark Mode
- Background: `#111827`
- Chat background: `#1F2937`
- AI message bubble: `#374151` (dark gray)
- User message bubble: `#6D28D9` (purple)
- Text: `#F9FAFB` (light gray)
- Accent: `#60A5FA` (light blue)
- Success: `#34D399` (light green)

---

## Special Features (Nice to Have)

1. **Message Actions**
   - Copy message text (on hover)
   - Regenerate AI response

2. **Session Management**
   - Save chat history to localStorage
   - Resume previous sessions
   - Export entire conversation

3. **Quick Actions**
   - "Start Over" button
   - "Example Agent" templates
   - Keyboard shortcuts (Cmd/Ctrl + Enter to send)

4. **Preview Modal**
   - Show generated prompt before download
   - Syntax highlighting for code
   - Copy to clipboard button

5. **Notifications**
   - Toast messages for downloads
   - Success/error notifications
   - "Copied!" feedback

---

## Example Component Structure

```
App
├── Header
│   ├── Logo
│   ├── NewChatButton
│   └── ThemeToggle
├── Sidebar (optional)
│   ├── ChatHistory
│   └── ExamplePrompts
├── ChatContainer
│   ├── ProgressIndicator
│   ├── MessageList
│   │   ├── MessageBubble (AI)
│   │   ├── MessageBubble (User)
│   │   └── TypingIndicator
│   ├── WorkflowPreview (conditional)
│   │   ├── MermaidDiagram
│   │   └── TextSummary
│   └── DownloadSection (conditional)
│       ├── FormatSelector
│       ├── ExportSelector
│       └── DownloadButton
└── InputArea
    ├── TextInput
    └── SendButton
```

---

## API Endpoints Reference

All endpoints use base URL: `http://localhost:8000/api/v1`

```javascript
// Create session
POST /sessions/create
Body: {}

// Send message
POST /sessions/{session_id}/message
Body: { message: string }

// Get workflow
GET /workflows/{session_id}/visualize

// Generate prompts
POST /prompts/{session_id}/generate
Body: { formats: string[] }

// Download export
GET /prompts/{session_id}/export/download?format={format}
```

---

## Sample Code Snippets

### Creating a Session
```javascript
async function createSession() {
  const response = await fetch('http://localhost:8000/api/v1/sessions/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  const data = await response.json();
  return {
    sessionId: data.session_id,
    initialMessage: data.message
  };
}
```

### Sending a Message
```javascript
async function sendMessage(sessionId, message) {
  const response = await fetch(
    `http://localhost:8000/api/v1/sessions/${sessionId}/message`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    }
  );
  const data = await response.json();
  return {
    aiResponse: data.ai_response,
    stage: data.stage,
    isComplete: data.is_complete
  };
}
```

### Downloading Export
```javascript
async function downloadExport(sessionId, format) {
  const url = `http://localhost:8000/api/v1/prompts/${sessionId}/export/download?format=${format}`;
  const response = await fetch(url);
  const blob = await response.blob();
  
  // Trigger download
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `agent.${format}`;
  link.click();
}
```

---

## Final Notes

### Priority Features (MVP)
1. ✅ Chat interface with message bubbles
2. ✅ API integration for conversation
3. ✅ Progress indicator
4. ✅ Workflow preview with Mermaid
5. ✅ Format selection and download

### Future Enhancements
- Chat history and session management
- Preview modal for generated prompts
- Export conversation as PDF
- Share agent configuration link
- Agent templates library

---

## Success Criteria

The frontend is successful when:
- ✅ User can have a complete conversation with the AI
- ✅ All messages display correctly in order
- ✅ Workflow diagram renders properly
- ✅ User can select format and download configuration
- ✅ Interface is intuitive and requires no instructions
- ✅ Works smoothly on mobile and desktop
- ✅ Handles errors gracefully

---

**Ready to build! Use this prompt with Bolt.new, v0.dev, or any AI frontend generator.**

