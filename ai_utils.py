import os
from huggingface_hub import InferenceClient
from google import genai
from dotenv import load_dotenv
from PIL import Image
import uuid
import io
import base64

load_dotenv()


# -------------------------------
# STORY GENERATION
# -------------------------------
def generate_story(prompt: str) -> str:
    """Generate a child-friendly story using Gemini API"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
    model="gemini-2.5-flash",
        contents=f"Write a magical, heartwarming, child-friendly story about: {prompt}."
    )

    # Defensive extraction of text from possible response shapes
    try:
        # Common attribute used by some SDK versions
        if hasattr(response, "text") and response.text:
            return response.text

        # SDKs sometimes return dict-like objects
        if isinstance(response, dict):
            # direct keys
            for key in ("text", "output_text", "content", "output"):
                if key in response and response[key]:
                    return response[key]

            # nested candidates/outputs
            for container in ("candidates", "outputs", "choices"):
                items = response.get(container)
                if items and isinstance(items, (list, tuple)) and len(items) > 0:
                    first = items[0]
                    if isinstance(first, dict):
                        for k in ("text", "content", "message", "output_text"):
                            if k in first and first[k]:
                                return first[k]

        # Fallback to string representation
        return str(response)
    except Exception:
        return str(response)

# -------------------------------
# IMAGE GENERATION
# -------------------------------
def generate_ghibli_image(prompt: str) -> str:
    """Generate a Ghibli-style image using free Hugging Face model"""
    image_prompt = f"{prompt}, Studio Ghibli style, soft lighting, warm colors, expressive eyes"
    try:
        result = InferenceClient(api_key=os.getenv("HF_TOKEN")).text_to_image(
    prompt=image_prompt,
            model="stabilityai/sdxl-turbo"  # Free model
        )
    except Exception as e:
        raise RuntimeError(f"Hugging Face image generation failed: {e}") from e

    # Normalize result into a PIL Image
    img = None
    try:
        # If the client returns raw bytes
        if isinstance(result, (bytes, bytearray)):
            img = Image.open(io.BytesIO(result))

        # If it returns a PIL Image-like object
        elif hasattr(result, "save"):
            img = result

        # If it returns a dict with base64 or bytes
        elif isinstance(result, dict):
            data = None
            for key in ("image", "images", "data", "b64_json"):
                if key in result and result[key]:
                    data = result[key]
                    break

            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            if isinstance(data, (bytes, bytearray)):
                img = Image.open(io.BytesIO(data))
            elif isinstance(data, str):
                # assume base64-encoded
                try:
                    img = Image.open(io.BytesIO(base64.b64decode(data)))
                except Exception:
                    # try to decode possible data URI
                    if data.startswith("data:"):
                        _, b64 = data.split(",", 1)
                        img = Image.open(io.BytesIO(base64.b64decode(b64)))
            else:
                raise RuntimeError("Unknown image content format in HF response")

        else:
            # Last resort: try to convert to bytes then open
            try:
                b = bytes(result)
                img = Image.open(io.BytesIO(b))
            except Exception:
                raise RuntimeError(f"Unsupported image result type: {type(result)}")

    except Exception as e:
        raise RuntimeError(f"Failed to parse image response: {e}") from e

    os.makedirs("images", exist_ok=True)
    filename = f"images/{uuid.uuid4().hex}.png"
    img.save(filename)
    return filename
