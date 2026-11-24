from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.concurrency import run_in_threadpool
from ai_utils import generate_story, generate_ghibli_image
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>CareTales</title>
<style>body{max-width:44rem;margin:3rem auto;padding:0 1rem;font:1rem/1.55 system-ui;color:#222;background:#f7f3e9}textarea,button{font:inherit;padding:.7rem}textarea{display:block;width:100%;box-sizing:border-box;margin:.5rem 0}button{background:#203b2c;color:white;border:0}img{max-width:100%;border-radius:.5rem}#story{white-space:pre-wrap}</style></head>
<body><main><h1>CareTales</h1><form id="form"><label for="prompt">What should the story be about?</label><textarea id="prompt" name="prompt" rows="4" required maxlength="1000"></textarea><button>Generate story and illustration</button></form><p id="status" role="status"></p><section id="story" aria-label="Generated story"></section><img id="illustration" alt="Generated story illustration" hidden></main>
<script>
const form = document.querySelector('#form');
const button = form.querySelector('button');
const status = document.querySelector('#status');
const story = document.querySelector('#story');
const illustration = document.querySelector('#illustration');
async function generate(path, body) {
  const response = await fetch(path, { method: 'POST', body });
  if (!response.ok) throw new Error('Generation failed');
  return response.json();
}
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const body = new FormData(form);
  if (!body.get('prompt').trim()) { status.textContent = 'Enter a story idea.'; return; }
  button.disabled = true;
  story.textContent = '';
  illustration.hidden = true;
  status.textContent = 'Writing your story…';
  try {
    story.textContent = (await generate('/generate-story', body)).story;
    status.textContent = 'Drawing your illustration…';
    illustration.src = (await generate('/generate-ghibli-image', body)).image_url;
    illustration.hidden = false;
    status.textContent = 'Your story and illustration are ready.';
  } catch {
    status.textContent = story.textContent ? 'Your story is ready. The illustration could not be generated.' : 'The story could not be generated. Please try again.';
  } finally { button.disabled = false; }
});
</script></body></html>''')


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
