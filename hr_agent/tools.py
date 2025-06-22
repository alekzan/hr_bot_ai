import base64
import json
import os
import sqlite3
import time

from vertexai.preview.vision_models import ImageGenerationModel

# --- GLOBAL CONFIGURATION (loaded once) ---
# These are loaded from the .env file by the ADK runner.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # Default if not set
DATABASE_FILE = "messages.db"
IMAGES_DIR = "generated_images"

# Ensure images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)

def create_image(tool_context, prompt: str) -> dict:
    """
    Generates two 3:4 images from a prompt using Imagen 4 and saves them locally,
    returning URLs instead of base64 data to prevent token accumulation.
    """
    # 1. Validate environment configuration
    if not PROJECT_ID or not LOCATION:
        error_msg = "GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION not configured."
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}

    print(f"Generating 2 images with prompt: '{prompt}' in project {PROJECT_ID} and location {LOCATION}")

    try:
        # 2. Initialize the Vertex AI model
        model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-06-06")

        # 3. Generate images
        response = model.generate_images(
            prompt=prompt,
            number_of_images=2,
            aspect_ratio="3:4",
        )

        # 4. Process response and save images locally
        image_urls = []
        timestamp = int(time.time())
        
        for i, image in enumerate(response.images):
            # Generate unique filename
            image_filename = f"{timestamp}_{i+1}.png"
            image_path = os.path.join(IMAGES_DIR, image_filename)
            
            # Save image
            image.save(location=image_path)
            
            # Create URL for serving
            image_url = f"/images/{image_filename}"
            image_urls.append(image_url)
            print(f"Saved image to {image_path}")

        # 5. Store only the URLs in session state
        tool_context.state["generated_image_urls"] = image_urls
        tool_context.state["last_image_generation"] = prompt

        success_msg = f"Successfully generated {len(image_urls)} images and saved locally."
        print(success_msg)
        return {"status": "success", "message": success_msg, "image_urls": image_urls}

    except Exception as e:
        error_msg = f"An unexpected error occurred during image generation: {e}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}


def list_submitted_messages() -> str:
    """Retrieves the full list of worker-submitted messages from the SQLite database."""
    try:
        # Check if database file exists
        if not os.path.exists(DATABASE_FILE):
            print(f"Database file {DATABASE_FILE} not found, falling back to test data")
            # Fallback to test_messages.json if database doesn't exist
            try:
                with open("test_messages.json", "r") as f:
                    messages = json.load(f)
                return json.dumps(messages)
            except (FileNotFoundError, json.JSONDecodeError):
                return json.dumps([{"content": "No messages available"}])
        
        # Read from SQLite database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT content FROM messages ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()
        
        # Format as expected by the agent (same as test_messages.json format)
        messages = [{"content": row[0]} for row in rows]
        
        if not messages:
            return json.dumps([{"content": "No messages have been submitted yet."}])
        
        print(f"Loaded {len(messages)} messages from database")
        return json.dumps(messages)
        
    except Exception as e:
        error_message = f"Error loading messages from database: {e}"
        print(f"ERROR: {error_message}")
        return json.dumps([{"content": f"Error retrieving messages: {str(e)}"}])