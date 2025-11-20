from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.concurrency import run_in_threadpool
from ai_utils import generate_story, generate_ghibli_image
import os

app = FastAPI()
print(">>> USING APP FILE:", __file__)

# -------------------------------
# STORY GENERATION ENDPOINT
# -------------------------------
@app.post("/generate-story")
async def story_endpoint(prompt: str = Form(...)):
    try:
        # generate_story is blocking — run in a threadpool
        story_text = await run_in_threadpool(generate_story, prompt)
        return {"story": story_text}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# -------------------------------
# IMAGE GENERATION ENDPOINT
# -------------------------------
@app.post("/generate-ghibli-image")
async def image_endpoint(prompt: str = Form(...)):
    try:
        # image generation can be slow/blocking — run in threadpool
        image_path = await run_in_threadpool(generate_ghibli_image, prompt)
        filename = os.path.basename(image_path)
        return {"image_url": f"/get-image/{filename}"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# -------------------------------
# SERVE GENERATED IMAGES
# -------------------------------
@app.get("/get-image/{filename}")
async def get_image(filename: str):
    # sanitize filename to avoid path traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("images", safe_filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    else:
        return JSONResponse(content={"error": "Image not found"}, status_code=404)
@app.get("/test")
async def test():
    return {"msg": "FastAPI is working!"}