## HR Bot AI System Summary

### Architecture Overview
**Tech Stack**: FastAPI + Google ADK + Imagen 4 + SQLite + HTML/JavaScript

### Core Components

#### 1. **Backend (FastAPI - `app.py`)**
- **Message Board API**: Anonymous message submission/retrieval using SQLite
- **HR Agent Chat API**: Interfaces with Google ADK for AI conversations
- **Image Serving**: Static file serving for generated posters
- **Session Management**: Unique sessions per conversation with auto-cleanup

#### 2. **AI Agent (`hr_agent/`)**
- **Agent**: Google ADK agent using gemini-2.0-flash model
- **Tools**: 
  - `list_submitted_messages`: Reads worker feedback from database
  - `create_image`: Generates professional cartoon posters via Imagen 4 API
- **Instructions**: Creates workplace-appropriate poster designs, calls image tool only once per request

#### 3. **Frontend (`static/`)**
- **Message Board** (`/`): Anonymous submission interface
- **HR Chat** (`/chat`): Real-time chat with image display, download buttons, cache-busting headers

### Key Features Implemented

#### **Image Generation System**
- **API**: Direct Imagen 4 calls with 3:4 aspect ratio, 2 images per request
- **Storage**: Local file system (`generated_images/`) instead of base64 to prevent token accumulation
- **Serving**: URL-based serving with download functionality
- **Session Management**: Images cleared per request to prevent persistence issues

#### **Session Management**
- **Unique IDs**: `hr_session_{timestamp}` and `hr_user_{timestamp}` per conversation
- **Auto-cleanup**: Keeps last 5 events when reaching 10 to prevent token limits
- **Recovery**: Automatic fresh session creation on token limit errors

#### **Database**
- **SQLite**: Simple message storage with timestamp tracking
- **API Endpoints**: Submit, retrieve, clear messages with proper error handling

### Critical Bug Fixes Resolved
1. **Token Accumulation**: Switched from base64 to file URLs
2. **Image Persistence**: Session state clearing + cache-busting headers
3. **Double Tool Calls**: Agent instructions to call create_image only once
4. **Session Contamination**: Unique user IDs per conversation

### Deployment Requirements for Google Cloud Run
- **Environment Variables**: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_API_KEY`
- **Dependencies**: `requirements.txt` with Google ADK, FastAPI, Imagen API libraries
- **File Storage**: Need persistent volume or Cloud Storage for `generated_images/`
- **Database**: SQLite works for MVP, consider Cloud SQL for production
- **Authentication**: gcloud auth or service account for Imagen API access

### API Endpoints
- `GET /` - Message board interface
- `GET /chat` - HR chat interface  
- `POST /api/submit` - Submit anonymous message
- `GET /api/messages` - Retrieve messages
- `POST /api/chat` - Chat with HR agent
- `POST /api/chat/new` - Start fresh conversation
- `GET /images/{filename}` - Serve generated images

The system is now fully functional with proper image generation, session management, and no persistence bugs. Ready for Docker containerization and Google Cloud Run deployment!