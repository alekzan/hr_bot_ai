from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime
from typing import List
import os
import time

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import our HR agent
from hr_agent.agent import root_agent

app = FastAPI(title="HR Agent Message Board", version="1.0.0")

# Database setup
DATABASE_FILE = "messages.db"

def init_database():
    """Initialize SQLite database with messages table."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database on startup
init_database()

# Session management
_session_initialized = False
_current_session_id = None
_current_user_id = None

# ADK Setup
APP_NAME = "hr_agent_app"

# Initialize session service and runner
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

async def get_or_create_session(force_new=False):
    """Get or create the session."""
    global _session_initialized, _current_session_id, _current_user_id
    
    # Create new session ID and user ID if needed
    if force_new or _current_session_id is None:
        timestamp = int(time.time())
        _current_session_id = f"hr_session_{timestamp}"
        _current_user_id = f"hr_user_{timestamp}"  # Unique user ID for each conversation
        _session_initialized = False
    
    if not _session_initialized:
        try:
            await session_service.create_session(app_name=APP_NAME, user_id=_current_user_id, session_id=_current_session_id)
            print(f"✅ ADK session created: {_current_session_id} for user: {_current_user_id}")
            _session_initialized = True
        except Exception as e:
            print(f"⚠️ Session creation failed, trying to get existing: {e}")
            try:
                await session_service.get_session(app_name=APP_NAME, user_id=_current_user_id, session_id=_current_session_id)
                print(f"✅ ADK session exists: {_current_session_id} for user: {_current_user_id}")
                _session_initialized = True
            except Exception as e2:
                print(f"❌ Session error: {e2}")
                raise e2
    
    return await session_service.get_session(app_name=APP_NAME, user_id=_current_user_id, session_id=_current_session_id)

# Pydantic models
class MessageSubmission(BaseModel):
    content: str

class Message(BaseModel):
    id: int
    content: str
    created_at: str

class MessageResponse(BaseModel):
    success: bool
    message: str
    data: List[Message] = []

class ChatRequest(BaseModel):
    message: str

# API Endpoints
@app.post("/api/submit", response_model=MessageResponse)
async def submit_message(submission: MessageSubmission):
    """Submit a new anonymous message."""
    if not submission.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (content) VALUES (?)",
            (submission.content.strip(),)
        )
        
        conn.commit()
        conn.close()
        
        return MessageResponse(
            success=True,
            message="Message submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/messages", response_model=List[Message])
async def get_messages():
    """Retrieve all messages in reverse chronological order."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, created_at 
            FROM messages 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = [
            Message(id=row[0], content=row[1], created_at=row[2])
            for row in rows
        ]
        
        return messages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/messages/json")
async def get_messages_for_agent():
    """Get messages in the format expected by the HR agent."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT content FROM messages ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()
        
        # Format as expected by the agent
        messages = [{"content": row[0]} for row in rows]
        
        return messages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/api/messages/clear")
async def clear_all_messages():
    """Clear all messages from the database (admin function)."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages")
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully deleted {deleted_count} messages",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    """Chat with the HR Agent."""
    global _current_session_id, _current_user_id  # Declare global at the start of function
    
    try:
        # Ensure session exists
        await get_or_create_session()
        
        # Clear images from previous conversation topics at the start of each new request
        current_session = await get_or_create_session()
        
        # Clear session history if it's getting too large (prevent token limit issues)
        if len(current_session.events) > 10:  # Keep only last 10 events
            current_session.events = current_session.events[-5:]  # Keep last 5
            print("🧹 Cleared old session events to prevent token limit")
        
        # Create user content 
        content = types.Content(role='user', parts=[types.Part(text=request.message)])
        
        # Run the agent using run_async
        events = []
        async for event in runner.run_async(user_id=_current_user_id, session_id=_current_session_id, new_message=content):
            events.append(event)
        
        # Extract the final response
        final_response = ""
        current_images = []  # Images for this specific response
        
        for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                break
        
        # Only get images if they were generated in this conversation turn
        # Check if the session state was updated during this request
        updated_session = await get_or_create_session()
        session_image_urls = updated_session.state.get("generated_image_urls", [])
        
        # Return image URLs only if they exist (meaning they were just generated)
        if session_image_urls:
            current_images = session_image_urls
            # Clear the image URLs from session state after returning them
            updated_session.state["generated_image_urls"] = []
        
        return {
            "response": final_response or "I received your message.",
            "images": current_images  # These are now URLs, not base64
        }
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        # If token limit exceeded, start fresh session
        if "token count" in str(e).lower() and "exceeds" in str(e).lower():
            try:
                print("🔄 Token limit exceeded, starting fresh session...")
                timestamp = int(time.time())
                _current_session_id = f"hr_session_{timestamp}"
                _current_user_id = f"hr_user_{timestamp}"
                await get_or_create_session(force_new=True)
                
                # Retry the request with fresh session
                content = types.Content(role='user', parts=[types.Part(text=request.message)])
                events = []
                async for event in runner.run_async(user_id=_current_user_id, session_id=_current_session_id, new_message=content):
                    events.append(event)
                
                final_response = ""
                for event in events:
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            final_response = event.content.parts[0].text
                        break
                
                updated_session = await get_or_create_session()
                session_image_urls = updated_session.state.get("generated_image_urls", [])
                current_images = []
                
                if session_image_urls:
                    current_images = session_image_urls
                    updated_session.state["generated_image_urls"] = []
                
                return {
                    "response": final_response or "I received your message. (Started fresh session due to size limit)",
                    "images": current_images
                }
            except Exception as retry_error:
                print(f"❌ Retry also failed: {retry_error}")
                return {
                    "response": "I'm having trouble processing your request right now. Please try using the 'New Chat' button to start fresh.",
                    "images": []
                }
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/new")
async def start_new_chat():
    """Start a fresh chat conversation."""
    try:
        # Force create a new session with new user ID
        session = await get_or_create_session(force_new=True)
        
        return {
            "success": True,
            "message": "New conversation started",
            "session_id": _current_session_id,
            "user_id": _current_user_id
        }
    except Exception as e:
        print(f"❌ Error starting new chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history():
    """Get the current chat history."""
    try:
        session = await get_or_create_session()
        
        # Extract chat messages from session events
        chat_messages = []
        for event in session.events:
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    text_content = ""
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_content += part.text
                    
                    if text_content.strip():
                        chat_messages.append({
                            "content": text_content.strip(),
                            "isUser": event.author == "user",
                            "images": []  # Images are not persisted in history
                        })
        
        return {
            "messages": chat_messages,
            "images": []  # No persistent images
        }
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        return {"messages": [], "images": []}

# Serve generated images first (more specific path)
app.mount("/images", StaticFiles(directory="generated_images"), name="images")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    """Serve the message board frontend."""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
        <body>
        <h1>HR Message Board</h1>
        <p>Frontend not found. Please create static/index.html</p>
        </body>
        </html>
        """)

@app.get("/chat", response_class=HTMLResponse)
async def serve_chat():
    """Serve the HR chat interface."""
    try:
        with open("static/chat.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
        <body>
        <h1>HR Chat Interface</h1>
        <p>Chat interface not found. Please create static/chat.html</p>
        <p><a href="/">← Back to Message Board</a></p>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 