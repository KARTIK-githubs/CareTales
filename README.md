# CareTales

A FastAPI prototype that turns a text prompt into a short illustrated story. It uses Gemini for story text and Hugging Face inference for images.

## Run locally

Install the dependencies from `requirements.txt`, then provide `GEMINI_API_KEY` and `HF_TOKEN` through your local environment. Start the API with `python -m uvicorn app:app --reload` and open `http://127.0.0.1:8000/docs`. The interactive API lists the story, illustration, and image retrieval routes.

[Original project and contributors](https://github.com/ayush-bhatt-07/CareTales)
