from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from meme_pipeline import MemePipeline

app = FastAPI(title="Multimodal Meme Generator API")

# ── CORS — allow all origins (needed for Live Server frontend) ───────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create output folder and serve it as static ──────────────────────────────
os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

# ── Pipeline ─────────────────────────────────────────────────────────────────
pipeline = MemePipeline()

class MemeRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"message": "Multimodal Meme Generator API is running!"}

@app.post("/generate")
def generate_meme(request: MemeRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        result = pipeline.run(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ping")
def ping():
    return {"status": "ok"}