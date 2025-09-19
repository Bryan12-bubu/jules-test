# Vertex AI Generative API Project

This project provides a simple yet powerful FastAPI service to generate images and videos using Google Cloud's Vertex AI models. It's built with modern Python tools like Poetry and FastAPI and includes a basic CI/CD pipeline.

A core feature of this project is its configuration-driven approach, allowing you to easily control which AI models are used, thereby managing your operational costs effectively.

## ✨ Features

-   **FastAPI Backend**: A robust, asynchronous API built with FastAPI.
-   **Cost Control**: Easily specify which Vertex AI models to use via a configuration file, giving you direct control over costs.
-   **Image Generation**: Endpoint to generate images from a text prompt.
-   **Video Generation**: A placeholder endpoint and structure for generating videos from text prompts.
-   **Poetry Dependency Management**: Modern, reliable package management.
-   **CI/CD Ready**: A GitHub Actions workflow is included for automated linting and testing.

## 셋업 (Setup)

### 1. Prerequisites

-   Python 3.12 or later
-   [Poetry](https://python-poetry.org/docs/#installation) for package management.
-   A Google Cloud Platform (GCP) project with the Vertex AI API enabled.
-   The `gcloud` command-line tool installed and authenticated.

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Install dependencies using Poetry:**
    This command will create a virtual environment in the project's directory (`.venv`) and install all necessary packages.
    ```bash
    poetry install
    ```

### 3. Google Cloud Authentication

For the service to access Vertex AI, you need to be authenticated. The recommended way is to use Application Default Credentials (ADC).

Run the following command and follow the login process in your browser:
```bash
gcloud auth application-default login
```

### 4. Configuration File

The application is configured using a `.env` file.

1.  **Create a `.env` file** by copying the example file:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** with your specific configuration:
    ```
    # Your Google Cloud Project ID
    GCP_PROJECT_ID="your-gcp-project-id-here"

    # The GCP region
    GCP_LOCATION="us-central1"

    # --- Model Selection for Cost Control ---
    IMAGE_GENERATION_MODEL="imagegeneration@006"
    VIDEO_GENERATION_MODEL="imagica@001" # Note: This is a placeholder!
    ```
    **Important:** You must replace `"your-gcp-project-id-here"` with your actual GCP Project ID. You can also change the model names to control costs or use different versions.

## 🚀 Running the Application

To run the FastAPI server locally, use `uvicorn`. Poetry makes this easy:

```bash
poetry run uvicorn src.app.main:app --reload
```

The server will be available at `http://127.0.0.1:8000`. The `--reload` flag enables hot-reloading for development.

## ⚙️ API Usage

You can interact with the API using tools like `curl` or by visiting the interactive documentation at `http://127.0.0.1:8000/docs`.

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://127.0.0.1:8000/health
```
**Expected Response:**
```json
{"status":"ok"}
```

### Generate an Image

**Endpoint:** `POST /generate/image`

This will generate an image and return it as a PNG file.

```bash
curl -X POST http://127.0.0.1:8000/generate/image \
-H "Content-Type: application/json" \
-d '{"prompt": "A futuristic city on Mars"}' \
--output mars_city.png
```
The generated image will be saved to `mars_city.png`.

### Generate a Video (Placeholder)

**Endpoint:** `POST /generate/video`

**Note:** This endpoint is a placeholder. You must configure a valid video model in your `.env` file for it to work.

```bash
curl -X POST http://127.0.0.1:8000/generate/video \
-H "Content-Type: application/json" \
-d '{"prompt": "A hummingbird flying in slow motion"}' \
--output placeholder_video.mp4
```
This will return a placeholder MP4 file.

## ✅ Testing and CI/CD

-   **Running Tests**: To run the test suite locally, use `pytest`:
    ```bash
    poetry run pytest
    ```

-   **CI/CD**: The repository includes a GitHub Actions workflow in `.github/workflows/ci.yml`. It automatically runs the linter (`ruff`) and the test suite on every push and pull request to the `main` branch.
