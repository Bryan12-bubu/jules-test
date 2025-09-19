import os
import uuid
import datetime
from contextlib import asynccontextmanager

import vertexai
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from vertexai.preview.vision_models import ImageGenerationModel

from app.config import settings

# --- FastAPI App Setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Initializes Vertex AI on startup.
    """
    print("Application startup...")
    print(f"Initializing Vertex AI for project '{settings.GCP_PROJECT_ID}' in '{settings.GCP_LOCATION}'")
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    print("Vertex AI initialized.")
    yield
    # Cleanup logic can go here if needed
    print("Application shutdown.")

app = FastAPI(
    title="Vertex AI Generative API",
    description="A FastAPI service to generate images and videos using Google Vertex AI.",
    version="0.1.0",
    lifespan=lifespan
)

# --- Pydantic Models for API ---

class GenerationRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The text prompt for generation.",
        examples=["A majestic lion in the savannah at sunset"]
    )

# --- Temporary File Management ---
# In a real production app, consider a more robust solution like a scheduled cleanup job
# or using a cloud storage bucket with lifecycle rules.
TEMP_DIR = "temp_output"
os.makedirs(TEMP_DIR, exist_ok=True)


# --- API Endpoints ---

@app.get("/health", summary="Health Check")
async def health_check():
    """
    Simple health check endpoint to confirm the service is running.
    """
    return {"status": "ok"}


@app.post("/generate/image", summary="Generate an Image")
async def generate_image(request: GenerationRequest):
    """
    Generates an image based on a text prompt.

    This endpoint uses the model specified by `IMAGE_GENERATION_MODEL` in your `.env` file.
    It returns the generated image as a PNG file.
    """
    try:
        print(f"Received image generation request with prompt: '{request.prompt}'")
        model = ImageGenerationModel.from_pretrained(settings.IMAGE_GENERATION_MODEL)

        print(f"Generating image using model '{settings.IMAGE_GENERATION_MODEL}'...")
        response = model.generate_images(
            prompt=request.prompt,
            number_of_images=1
        )

        image = response[0]

        # Save image to a temporary file
        filename = f"img_{uuid.uuid4()}.png"
        output_path = os.path.join(TEMP_DIR, filename)
        image.save(location=output_path)
        print(f"Image saved temporarily to '{output_path}'")

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
    """
    Generates a video based on a text prompt.

    **IMPORTANT NOTE:** This is a **placeholder** implementation. The Vertex AI
    Text-to-Video API is not as straightforward as the image generation one as of late 2023.

    To make this work, you must:
    1. Find an available Text-to-Video model in the Vertex AI Model Garden.
    2. Update the `VIDEO_GENERATION_MODEL` in your `.env` file with the correct model identifier.
    3. The code below assumes a similar SDK interface to the image model. You may need to
       adjust the `vertexai.preview.vision_models` import and the model calling method
       based on the specific video model's documentation.
    """
    print(f"Received video generation request with prompt: '{request.prompt}'")
    print("!!! WARNING: This endpoint is a placeholder and may not work without a valid model !!!")

    try:
        # --- Placeholder Code ---
        # The following lines are a template. You will likely need to change them.
        # from vertexai.preview.vision_models import VideoGenerationModel # This might not be the correct class

        print(f"Attempting to use video model '{settings.VIDEO_GENERATION_MODEL}'...")
        # model = VideoGenerationModel.from_pretrained(settings.VIDEO_GENERATION_MODEL)
        # response = model.generate_videos(prompt=request.prompt) # Method name is a guess
        # video = response[0]

        # Since the above is a placeholder, we will simulate a file creation for now.
        # Replace this with the actual video saving logic.
        filename = f"vid_{uuid.uuid4()}.mp4"
        output_path = os.path.join(TEMP_DIR, filename)

        # --- SIMULATED FILE ---
        # In a real implementation, you would save the video content here.
        # e.g., video.save(location=output_path)
        with open(output_path, "w") as f:
            f.write(f"This is a placeholder video for prompt: {request.prompt}")
        print(f"Placeholder video saved temporarily to '{output_path}'")
        # --- END SIMULATION ---

        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=f"generated_video_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.mp4"
        )

    except Exception as e:
        print(f"An error occurred during video generation: {e}")
        # This will likely fail if the model name is just a placeholder.
        raise HTTPException(status_code=501, detail=f"Video generation is not implemented or failed: {e}")
