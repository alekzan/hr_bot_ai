
import os
from dotenv import load_dotenv
from google.adk.agents import Agent

# --- IMPORTACIONES ---
# Importamos todos los subagentes
from example_sub_agent import intake_agent

# Importar herramientas SOLO del orquestador (get/update stage)
from .tools import is_intake_completed

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "TU_API_KEY_DE_GOOGLE_AI_STUDIO":
    print(
        "ADVERTENCIA: GOOGLE_API_KEY no está configurada o sigue siendo el placeholder en .env"
    )
    
# -- MODELOS IA DISPONIBLES --
GEMINI_FLASH = "gemini-2.0-flash"
model_name = GEMINI_FLASH

OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    model=model_name,
    description="Routes users to the intake process or the CRM structure building pipeline based on intake completion status.",
    instruction="""You are the Orchestrator. Your sole responsibility is to direct the user to the correct phase of the CRM structure setup process. Do not attempt to handle any user requests yourself, other than initial greetings or phase transition messages.

    YOUR PROCESS:
    1.  **Call the `is_intake_completed` tool.** This tool will tell you if the user has successfully completed the initial intake process.
    2.  **Analyze the tool's result:**
        *   If the tool returns "TRUE":
            a.  You MUST **DELEGATE** the conversation to the `sequential_agent` to begin the automated structure building pipeline.
            b.  Your task for this turn is finished.
        *   If the tool returns "FALSE":
            a.  Regardless of whether it's the first message or a subsequent one while intake is False (pending), you MUST **DELEGATE** the conversation to the `intake_agent`. The `intake_agent` is designed to handle the multi-turn conversation for collecting information.
            b.  Your task for this turn is finished.

    SUBAGENT DETAILS (for your routing context):
    *   `intake_agent`: Handles the multi-turn conversation to collect necessary business information from the user.
    *   `sequential_agent`: Executes the automated sequence of steps to design CRM stages, create agent prompts, and select fields/tags, once intake is complete.

    IMPORTANT: Always rely on the `is_intake_completed` tool to determine the current phase. Once you delegate, the subagent takes over for that turn.
    """,
    # HERRAMIENTAS SOLO DEL ORQUESTADOR
    tools=[
        is_intake_completed,
    ],
    # LISTA FINAL DE SUBAGENTES
    sub_agents=[intake_agent],
)

print(
    "OrchestratorAgent definido con todos los subagentes: Training, QuizEvaluator y Doubt."
)

# El agente raíz sigue siendo el Orquestador
root_agent = OrchestratorAgent