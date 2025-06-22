import base64
import json
import os
import requests
import sqlite3
import uuid
import time

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

    # 2. Get a fresh gcloud access token
    try:
        token_command = "gcloud auth print-access-token"
        access_token = os.popen(token_command).read().strip()
        if not access_token:
            raise ValueError("Token is empty. Is gcloud authenticated?")
    except Exception as e:
        error_msg = f"Error obtaining gcloud access token: {e}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}

    print(f"Generating 2 images with prompt: '{prompt}'")

    # 3. Prepare and make the API request
    try:
        api_url = (
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/"
            f"{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/"
            "imagen-4.0-generate-preview-06-06:predict"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 2, "aspectRatio": "3:4"},
        }

        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Check for HTTP errors
        response_json = response.json()

        if "predictions" not in response_json or not response_json["predictions"]:
            raise ValueError("API response did not contain predictions.")

        # 4. Process response and save images locally
        image_urls = []
        timestamp = int(time.time())
        
        for i, prediction in enumerate(response_json["predictions"]):
            # Generate unique filename
            image_filename = f"{timestamp}_{i+1}.png"
            image_path = os.path.join(IMAGES_DIR, image_filename)
            
            # Decode and save image
            image_data = base64.b64decode(prediction["bytesBase64Encoded"])
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            # Create URL for serving
            image_url = f"/images/{image_filename}"
            image_urls.append(image_url)
            print(f"Saved image to {image_path}")

        # 5. Store only the URLs in session state (no base64!)
        tool_context.state["generated_image_urls"] = image_urls
        tool_context.state["last_image_generation"] = prompt

        success_msg = f"Successfully generated {len(image_urls)} images and saved locally."
        print(success_msg)
        return {"status": "success", "message": success_msg, "image_urls": image_urls}

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP Error: {http_err.response.status_code} {http_err.response.text}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
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