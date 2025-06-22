import os
import requests
import json
import base64
import uuid
from dotenv import load_dotenv

# --- GLOBAL CONFIGURATION (loaded once at script startup) ---
load_dotenv()  # Loads environment variables from the .env file

# Ensure these variables are set in your .env or accessible in your environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") # E.g., "us-central1"

# Directory where generated images will be saved
IMAGE_DIR = "generated_images"

# --- IMAGE GENERATION FUNCTION ---

def create_image(
    prompt: str,
    model_name: str = "imagen-4.0-generate-preview-06-06",
    aspect_ratio: str = "3:4" # New parameter for aspect ratio, default to 1:1
) -> dict:
    """
    Generates an image from a text prompt using Vertex AI Imagen model
    via a direct API call (using the 'requests' library).

    Args:
        prompt (str): The text describing the image to generate.
        model_name (str, optional): The name of the Imagen model to use.
                                    Defaults to "imagen-4.0-generate-preview-06-06".
                                    Consider "imagen-2.0" for the GA model,
                                    or other preview names if you have access.
        aspect_ratio (str, optional): The desired aspect ratio for the generated image.
                                      Supported values: "1:1", "3:4", "4:3", "16:9", "9:16".
                                      Defaults to "1:1" (square).

    Returns:
        dict: A dictionary with the key 'image_path' (path to the saved file) on success,
              or with the key 'error' and an error message on failure.
    """
    # 1. Validate global configuration
    if not PROJECT_ID or not LOCATION:
        return {"error": "Error: GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION environment variables are not configured."}

    # 2. Obtain gcloud access token
    # This is executed for each function call to ensure a fresh token.
    # In high-concurrency scenarios, token caching might be considered for optimization.
    try:
        access_token = os.popen('gcloud auth print-access-token').read().strip()
        if not access_token:
            raise ValueError("Could not get gcloud access token. Are you authenticated?")
    except Exception as e:
        return {"error": f"Error obtaining gcloud access token: {e}. Please ensure 'gcloud auth application-default login' is run in your terminal."}

    print(f"Generating image with prompt: '{prompt}' using model: '{model_name}' and aspect ratio: '{aspect_ratio}'")

    try:
        # 3. Create the image directory if it doesn't exist
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
            print(f"Directory created: {IMAGE_DIR}")

        # 4. Generate a unique filename to avoid overwriting
        image_filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(IMAGE_DIR, image_filename)

        # 5. Configure the API endpoint URL
        publisher_name = "google"
        api_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/{publisher_name}/models/{model_name}:predict"

        # 6. Prepare the JSON payload
        payload = {
            "instances": [
                {"prompt": prompt}
            ],
            "parameters": {
                "sampleCount": 2, # Generating one image per call
                "aspectRatio": aspect_ratio # Add the aspect ratio parameter here
            }
        }

        # 7. Configure HTTP headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        # 8. Make the HTTP POST call
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json() # Parse the JSON response from the server

        # 9. Process the response and save the image
        if "predictions" in response_json and response_json["predictions"]:
            image_data_base64 = response_json["predictions"][0]["bytesBase64Encoded"]
            image_bytes = base64.b64decode(image_data_base64)

            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Image saved successfully to {output_path}")
            return {"image_path": output_path}
        else:
            return {"error": "No valid image predictions received from the API response."}

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP Error during image generation (Status: {http_err.response.status_code}): {http_err.response.text}"
        print(f"❌ {error_message}")
        return {"error": error_message}
    except requests.exceptions.RequestException as req_err:
        error_message = f"Network or request error during image generation: {req_err}"
        print(f"❌ {error_message}")
        return {"error": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred during image generation: {e}"
        print(f"❌ {error_message}")
        return {"error": error_message}

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    print("--- Testing the create_image function ---")
    
    # Example 1: Generate an image with 3:4 aspect ratio
    result1 = create_image(prompt="A mystical forest with glowing mushrooms, hyper realistic", aspect_ratio="3:4")
    if "image_path" in result1:
        print(f"Result 1: Success! Image at: {result1['image_path']}")
    else:
        print(f"Result 1: Error! {result1['error']}")

    print("\n--- Testing with default 1:1 aspect ratio ---")
    result2 = create_image(prompt="A majestic lion on a savanna, sunny day, wide shot")
    if "image_path" in result2:
        print(f"Result 2: Success! Image at: {result2['image_path']}")
    else:
        print(f"Result 2: Error! {result2['error']}")

    print("\n--- Testing a failed attempt (e.g., empty prompt) ---")
    result3 = create_image(prompt="") # An empty prompt might lead to an API error or invalid generation
    print(f"Result 3: {result3}")