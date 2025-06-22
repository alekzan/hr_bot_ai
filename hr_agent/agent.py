import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from .tools import (
    create_image,
    list_submitted_messages,
)

# Importamos todos los subagentes


# Importar herramientas SOLO del orquestador (get/update stage)
# from .tools import ...

load_dotenv()

# Ensure API key is set, but don't print warnings in production
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or "YOUR_API_KEY" in api_key:
    print(
        "WARNING: GOOGLE_API_KEY is not set or is using a placeholder in .env"
    )

# -- MODELOS IA DISPONIBLES --
GEMINI_FLASH = "gemini-2.0-flash"
model_name = GEMINI_FLASH

root_agent = Agent(
    name="hr_agent",
    model=model_name,
    description=(
        "The HR Agent assists HR staff by:\n"
        "- Reading submitted messages from workers (stored in session state)\n"
        "- Summarizing insights from these messages\n"
        "- Detecting recurring patterns or common complaints\n"
        "- Offering suggestions for action\n"
        "- Creating HR campaign images or posters with appropriate messaging"
    ),
    instruction=(
        "You are a helpful and proactive HR assistant. Your goal is to analyze "
        "messages from workers, identify patterns, and help create "
        "communication materials. Before answering any question about "
        "worker messages, you MUST first use the `list_submitted_messages` "
        "tool to retrieve the data. When asked to create a poster or image, "
        "you MUST use the `create_image` tool. Do not ask the user for "
        "information you can find yourself using your tools."
    ),
    tools=[
        list_submitted_messages,
        create_image,
    ],
)

print(
    "Supervisor Agent defined with subagentes: Sub Agent and Designer."
)