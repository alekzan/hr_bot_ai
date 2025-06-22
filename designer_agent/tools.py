from typing import List, Dict, Any, Optional
from google import genai
from google.adk.tools.tool_context import ToolContext

client = genai.Client()

def create_image(tool_context: ToolContext, prompt) -> str:
    """
    Creates an image using Image 4 in Vertex AI
    """
    # Retrieve data from the state. Optional
    # messages = tool_context.state.get("submitted_messages", [])
    
    # Makes call to Imagen 4 API
    image = client.models.generate_images(model="imagen-4.0-generate-preview-06-06", prompt=prompt,)
    
    # do we assign a name?
    # output_file = "output-image.png"
    #image.generated_images[0].image.save(output_file)
    
    # Return SOMEHOW the image
    return image