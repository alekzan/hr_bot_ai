### `README.md` — HR Agent (MVP) using Google ADK

#### 🌟 **Project Goal**
Build an MVP HR Agent using the **ADK (Agent Developer Kit)** framework. The agent will assist HR professionals by analyzing messages submitted by workers, summarizing them, identifying patterns, and generating image-based materials (e.g. posters) to support internal HR communication.

This agent will be deployed using **Google’s Agent Engine** and will rely on custom tools defined below.

---

### 🧠 **Agent Description**
**Agent Name:** `HR Agent`

**Purpose:**  
The HR Agent assists HR staff by:
- Reading submitted messages from workers (stored in session state)
- Summarizing insights from these messages
- Detecting recurring patterns or common complaints
- Offering suggestions for action
- Creating HR campaign images or posters with appropriate messaging

This is a **single-agent** architecture (no agent teams for now).

---

### 🛠️ **Tools**

#### `list_submitted_messages`
**Description:** Retrieves the full list of worker-submitted messages currently stored in the session state.  
**Usage:**  
Used by the agent to analyze, summarize, or identify trends in submissions.

**Input:** None  
**Output (example):**
```json
[
  {"content": "Someone keeps leaving dirty dishes in the sink."},
  {"content": "We should have flexible hours on Fridays."}
]
```

---

#### `create_image`
**Description:** Generates an image or poster based on input text prompt, connected to Google Imagen 4 or similar image model.  
**Usage:**  
Used to create printable/internal campaign posters for awareness (e.g. hygiene, teamwork, respect).

**Input (example):**
```json
{"prompt": "Create a poster that encourages cleanliness in the office kitchen."}
```

**Output (example):**
```json
{"image_url": "https://storage.googleapis.com/.../poster_cleanliness_123.png"}
```

---

### ⚙️ **Framework & Requirements**

We are using the [Google ADK Quickstart](https://google.github.io/adk-docs/get-started/quickstart/) to build and deploy this agent.

**Required packages (in `requirements.txt`):**
```text
google-cloud-aiplatform[adk,agent_engines]==1.97.0
google-adk==1.3.0
pydantic==2.11.4
google-api-python-client==2.172.0
google-genai==1.20.0
python-dotenv
```

Useful references:
- [Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
- [Agent Team Guide](https://google.github.io/adk-docs/tutorials/agent-team/)
- [Function & Tools Guide](https://google.github.io/adk-docs/tools/function-tools/)
- [Deploy to Agent Engine](https://google.github.io/adk-docs/deploy/agent-engine/)

---

### 🚀 **Deployment**

The agent must be prepared to deploy using the Agent Engine. Follow this guide:
📄 https://google.github.io/adk-docs/deploy/agent-engine/

Ensure:
- The agent is serializable
- Tools are registered using the ADK's tool interface
- Session state is respected (messages will be stored/retrieved from it)
- The agent is structured for long-running sessions (multiple queries from HR staff)

---

### 🧪 **Testing Suggestions (MVP)**

Examples of agent prompts to test:
- “Summarize all the messages submitted last week”
- “Are there any recurring complaints?”
- “Generate a poster reminding people to clean up after using the kitchen”

