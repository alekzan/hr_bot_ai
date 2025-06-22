## 📝 PRD — HR Agent MVP (Hackathon Version)

### 🌟 Objective

Build a simple web app with two sections:

1. **Anonymous Message Board** for workers to submit feedback.
2. **HR Agent Chat Interface** for HR to analyze, summarize, and request images.

---

### 📦 Stack

- **Frontend:** React + TailwindCSS (or plain HTML/CSS if time-constrained)
- **Backend:** Python (FastAPI or Flask)
- **LLM Agent:** Google ADK Agent Engine
- **Image Generator:** Google Imagen 4 (via `create_image` tool)
- **State Storage:** In-memory list or lightweight DB (e.g. SQLite or JSON file for hackathon)

---

## 🧹 Functional Requirements

### 🔹 Section 1: Anonymous Message Board

**Purpose:** Let workers anonymously submit feedback or complaints. Display them all in one place.

#### Features:

- Text input box (textarea)
- “Submit” button
- POST to backend and store in memory/JSON
- Display all submitted messages (reverse chronological order)
- No user login, no usernames
- No filtering, no tags (keep it simple)

#### Example Message:

> “Someone keeps leaving food in the fridge for weeks.”

---

### 🔹 Section 2: HR Agent Chat

**Purpose:** Allow HR team to interact with the AI assistant.

#### Features:

- Chat interface (text input, send button, chat bubble display)
- Send message to backend → forward to deployed **HR Agent** (ADK)
- Show agent responses in chat view
- If agent response contains image prompts:
  - Call `create_image` once. A single call will generate two images.
  - Show both 3:4 ratio images in chat
- Static 3:4 ratio enforcement (e.g. 768x1024)

---

## 🚀 Deliverables in 1 Hour

| Task                            | Owner / Notes                         |
| ------------------------------- | ------------------------------------- |
| Basic frontend UI (2 sections)  | React (Vite) or HTML/CSS              |
| Backend endpoints               | FastAPI or Flask (`/submit`, `/chat`) |
| In-memory or file-based storage | List or JSON                          |
| Chat call to ADK Agent          | REST API call                         |
| `create_image` integration      | Simulate or call real tool            |

---

## 🧪 Example Flows

### 1. Worker submits a message:

- Worker types “The kitchen smells awful.”
- Clicks "Submit"
- Message appears on the board below

### 2. HR sends a chat:

- HR types: “What are the main complaints?”
- Agent replies: “Most messages refer to cleanliness issues in shared spaces.”
- HR types: “Generate a kitchen cleanliness poster.”
- Two 3:4 images appear in chat view

