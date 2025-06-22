import os  # <-- Añadir
from google.adk.agents import Agent
from dotenv import load_dotenv  # <-- Añadir
from .tools import create_image


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "TU_API_KEY_DE_GOOGLE_AI_STUDIO":
    print(
        "ADVERTENCIA: GOOGLE_API_KEY no está configurada o sigue siendo el placeholder en .env"
    )
    
# AI models available
LL_MODEL = "gemini-2.0-flash"
model_name = LL_MODEL

designer_agent = Agent(
    name="designer_agent",
    model=model_name,  
    description="",
    # Instructions
    instruction="",
    # Saves the intake data using the tool
    tools=[
        create_image
    ],
)

print("intake_agent definido.")

root_agent = designer_agent