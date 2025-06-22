import base64
import json
import os
import requests
import uuid

# --- GLOBAL CONFIGURATION (loaded once) ---
# These are loaded from the .env file by the ADK runner.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # Default if not set


def create_image(tool_context, prompt: str) -> dict:
    """
    Generates two 3:4 images from a prompt using Imagen 4 and stores their
    base64 data in the session state.
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

        # 4. Process response and update session state
        new_images_b64 = [
            p["bytesBase64Encoded"] for p in response_json["predictions"]
        ]

        # Get existing images from state and append new ones
        current_images = tool_context.state.get("generated_images_b64", [])
        updated_images = current_images + new_images_b64
        
        # Keep only the last 2 images
        tool_context.state["generated_images_b64"] = updated_images[-2:]

        success_msg = f"Successfully generated {len(new_images_b64)} images and updated session state."
        print(success_msg)
        return {"status": "success", "message": success_msg}

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP Error: {http_err.response.status_code} {http_err.response.text}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}


def list_submitted_messages() -> str:
    """Retrieves the full list of worker-submitted messages from the JSON file."""
    try:
        with open("test_messages.json", "r") as f:
            messages = json.load(f)
        return json.dumps(messages)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        error_message = f"Error loading test_messages.json: {e}"
        return json.dumps(
            {"error": "Could not retrieve messages.", "details": str(e)}
        )