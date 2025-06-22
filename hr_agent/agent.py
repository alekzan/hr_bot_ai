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
    instruction = (
        "You are an HR Agent that helps analyze workplace feedback and create professional poster designs.\n"
        "Your main responsibilities:\n"
        "1. Analyze worker-submitted messages to identify workplace issues and trends\n"
        "2. Create professional, cartoon-style flat posters that address workplace concerns\n"
        "3. Provide helpful suggestions for improving workplace culture\n"
        "When users request posters or images:\n"
        "- ALWAYS use the create_image tool when asked to create a poster or image\n"
        "- Call the create_image tool ONLY ONCE per user request (it automatically generates 2 variations)\n"
        "- If a user says 'create a poster' or similar, you MUST call the create_image tool\n"
        "- Design flat, PROFESSIONAL cartoon-style posters with clean, modern aesthetics\n"
        "- Avoid mockups, renders, hanging clips, shadows, or angled displays\n"
        "- Use sophisticated color palettes (avoid overly bright or childish colors)\n"
        "- Include clear, concise messaging that's appropriate for a professional workplace\n"
        "- Create layouts that look suitable for direct print or digital display (bulletin boards, office TVs, etc.)\n"
        "- Use friendly but mature cartoon illustrations (think corporate mascots, not children's book characters)\n"
        "- Ensure text is readable and professionally formatted\n"
        "- The final output should appear as a complete flat poster, not a product showcase or 3D render\n"
        "IMPORTANT: When you generate images, DO NOT mention the image URLs in your response.\n"
        "Simply describe what you've created and let the images speak for themselves.\n"
        "Example response style:\n"
        "\"I've created two professional flat poster designs to address the noise concerns. These feature clean cartoon illustrations with clear messaging to help maintain a respectful workspace environment.\"\n"
        "Always be helpful, professional, and focused on creating solutions that improve workplace harmony."
    ),
    tools=[
        list_submitted_messages,
        create_image,
    ],
)

print(
    "Supervisor Agent defined with subagentes: Sub Agent and Designer."
)