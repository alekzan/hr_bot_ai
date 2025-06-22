# intake_agent/tools.py

import uuid
from typing import List, Dict, Any, Optional
from google.adk.tools.tool_context import ToolContext

def create_uuid_tool() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())

def intake_data(
    biz_name: str,
    biz_info: str,
    goal: str,
    kb_files: Optional[List[str]],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Save the intake data under a single 'pipeline' bucket in session state.
    
    Args:
        biz_name: Name of the business.
        biz_info: Description of the business.
        goal: Main goal for implementing the CRM.
        kb_files: List of uploaded knowledge base files (can be None).

    Returns:
        A dict with status and message.
    """
    print("Tool: intake_data called")

    # 1) Validate all required fields
    if not biz_name or not biz_info or not goal:
        return {"status": "error", "message": "Missing biz_name, biz_info or goal."}

    # 2) Normalize kb_files to an empty list if it's None or falsey
    kb_files_list: List[str] = kb_files or []

    # 3) Retrieve or generate business_id
    existing = tool_context.state.get("pipeline", {}).get("intake_data", {})
    business_id = existing.get("business_id") or create_uuid_tool()

    # 4) Save all to pipeline
    tool_context.state["pipeline"] = {
        "intake_data": {
            "business_id": business_id,
            "biz_name": biz_name,
            "biz_info": biz_info,
            "goal": goal,
            "kb_files": kb_files_list
        },
        "stages": {},
        "pipeline_completed": False
    }

    return {"status": "success", "message": "Intake data saved."}



# ⚠️ IMPORTANT: Here we removed the await keyword from the available files listing function: available_files = await tool_context.list_artifacts()
def list_uploaded_files_tool(tool_context: ToolContext) -> str:
    """
    Lists the documents the user has uploaded (tracked in session.state['uploaded_docs']).
    """
    uploaded = tool_context.state.get("uploaded_docs", [])
    if not uploaded:
        return "You have not uploaded any documents yet."
    # Format each filename on its own line
    file_list = "\n".join(f"- {name}" for name in uploaded)
    return f"Here are the documents the user have uploaded:\n{file_list}"


# This function would typically be wrapped in a FunctionTool
# from google.adk.tools import FunctionTool
# list_files_tool = FunctionTool(func=list_user_files_py)