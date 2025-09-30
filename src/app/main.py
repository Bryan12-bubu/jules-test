import os
import uuid
import time
import asyncio
import datetime
from contextlib import asynccontextmanager

import vertexai
from fastapi import FastAPI, HTTPException, Body
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from vertexai.preview.vision_models import ImageGenerationModel

from app.config import settings

# --- Constants ---
TEMP_DIR = "temp_output"
CLEANUP_INTERVAL_SECONDS = 3600  # 1 hour
MAX_FILE_AGE_SECONDS = 7200      # 2 hours

# --- Background Task for Cleanup ---

def cleanup_temp_files():
    """Scans the temporary directory and deletes files older than MAX_FILE_AGE_SECONDS."""
    now = time.time()
    deleted_count = 0
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > MAX_FILE_AGE_SECONDS:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted old temp file: {file_path}")
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
    if deleted_count > 0:
        print(f"Background cleanup finished. Deleted {deleted_count} file(s).")

async def periodic_cleanup():
    """Runs the cleanup task periodically in the background."""
    while True:
        print("Running periodic background cleanup...")
        await run_in_threadpool(cleanup_temp_files)
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


# --- FastAPI App Setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    - Initializes Vertex AI on startup.
    - Starts the background file cleanup task.
    """
    print("Application startup...")
    # Initialize Vertex AI
    print(f"Initializing Vertex AI for project '{settings.GCP_PROJECT_ID}' in '{settings.GCP_LOCATION}'")
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    print("Vertex AI initialized.")
    # Start background tasks
    asyncio.create_task(periodic_cleanup())
    yield
    # Cleanup logic can go here if needed
    print("Application shutdown.")

app = FastAPI(
    title="Vertex AI Generative API",
    description="A FastAPI service to generate images and videos using Google Vertex AI.",
    version="0.2.0",
    lifespan=lifespan
)

# --- Pydantic Models for API ---

class GenerationRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The text prompt for generation.",
        examples=["A majestic lion in the savannah at sunset"]
    )

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)


# --- API Endpoints ---

@app.get("/health", summary="Health Check")
async def health_check():
    """Simple health check endpoint to confirm the service is running."""
    return {"status": "ok"}


@app.post("/generate/image", summary="Generate an Image")
async def generate_image(request: GenerationRequest):
    """Generates an image based on a text prompt using non-blocking calls."""
    try:
        print(f"Received image generation request with prompt: '{request.prompt}'")

        def _generate_and_save():
            model = ImageGenerationModel.from_pretrained(settings.IMAGE_GENERATION_MODEL)
            print(f"Generating image using model '{settings.IMAGE_GENERATION_MODEL}'...")
            response = model.generate_images(prompt=request.prompt, number_of_images=1)
            image = response[0]
            filename = f"img_{uuid.uuid4()}.png"
            output_path = os.path.join(TEMP_DIR, filename)
            print(f"Saving image to '{output_path}'...")
            image.save(location=output_path)
            print(f"Image saved temporarily to '{output_path}'")
            return output_path

        output_path = await run_in_threadpool(_generate_and_save)

        return FileResponse(
            path=output_path,
            media_type="image/png",
            filename=f"generated_image_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.png"
        )
    except Exception as e:
        print(f"An error occurred during image generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/video", summary="Generate a Video (Placeholder)")
async def generate_video(request: GenerationRequest):
    """Generates a video based on a text prompt using non-blocking calls."""
    print(f"Received video generation request with prompt: '{request.prompt}'")
    print("!!! WARNING: This endpoint is a placeholder !!!")
    try:
        def _create_placeholder_video():
            filename = f"vid_{uuid.uuid4()}.mp4"
            output_path = os.path.join(TEMP_DIR, filename)
            with open(output_path, "w") as f:
                f.write(f"This is a placeholder video for prompt: {request.prompt}")
            print(f"Placeholder video saved temporarily to '{output_path}'")
            return output_path

        output_path = await run_in_threadpool(_create_placeholder_video)

        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=f"generated_video_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.mp4"
        )
    except Exception as e:
        print(f"An error occurred during video generation: {e}")
        raise HTTPException(status_code=501, detail=f"Video generation is not implemented or failed: {e}")
