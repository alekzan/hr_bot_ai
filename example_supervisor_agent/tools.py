from google.adk.tools.tool_context import ToolContext

def is_intake_completed(tool_context: ToolContext) -> bool:
    """
    Retrieves the value of 'intake_completed' from the session state.
    If it is not True, it is assigned as False in the state.

    Returns:
        bool: True if intake is completed, False otherwise.
    """
    print("Tool: is_intake_completed called")

    intake_completed = tool_context.state.get("intake_completed")

    if intake_completed is not True:
        intake_completed = False
        tool_context.state["intake_completed"] = False

    print(f"Intake completed status from state: {intake_completed}")
    return intake_completed