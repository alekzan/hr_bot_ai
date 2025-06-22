from typing import List, Dict, Any, Optional
from google.adk.tools.tool_context import ToolContext

def list_submitted_messages(tool_context: ToolContext) -> str:
    """
    Lists the submitted messages from the workers.
    """
    messages = tool_context.state.get("submitted_messages", [])
    if not messages:
        return "You have not submitted messages yet."
    # Format each filename on its own line
    messages_list = "\n".join(f"- {message}" for message in messages)
    return f"Here are the documents the user have uploaded:\n{messages_list}"