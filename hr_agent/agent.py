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
        "tool to retrieve the data. \n\n"
        "When asked to create a poster or image, you MUST use the `create_image` tool. "
        "IMPORTANT: Create simple, cartoon-style poster designs with:\n"
        "1. A colorful, fun CARTOON ILLUSTRATION as the main visual element\n"
        "2. ONE CLEAR, SHORT MESSAGE or slogan (not bullet points or lists)\n"
        "3. Bright, friendly colors and simple design\n"
        "4. Professional but approachable cartoon style\n\n"
        "Example format: 'Create a cartoon-style poster design with a bright blue background. "
        "Show a happy cartoon character (like a smiling dish or cleaning mascot) in the center. "
        "At the top, include the text \"KEEP OUR KITCHEN CLEAN!\" in large, bold, friendly letters. "
        "The overall design should be colorful, simple, and eye-catching like a friendly reminder poster.'\n\n"
        "Focus on creating ONE main message with a supporting cartoon illustration. "
        "The poster should be simple, memorable, and have a positive, encouraging tone. "
        "Avoid complex layouts, multiple bullet points, or realistic photography. "
        "Think of it like a motivational poster with a cartoon mascot and a simple slogan.\n\n"
        "Do not ask the user for information you can find yourself using your tools."
    ),
    tools=[
        list_submitted_messages,
        create_image,
    ],
)

print(
    "Supervisor Agent defined with subagentes: Sub Agent and Designer."
)