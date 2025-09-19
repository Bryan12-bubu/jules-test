from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It loads settings from a .env file and environment variables.
    """
    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- GCP Settings ---
    GCP_PROJECT_ID: str
    GCP_LOCATION: str = "us-central1"

    # --- Model Selection for Cost Control ---
    # User can define which models to use here to control costs.
    # These are example model names and might need to be updated based on
    # available Vertex AI models.
    IMAGE_GENERATION_MODEL: str = "imagegeneration@006"
    VIDEO_GENERATION_MODEL: str = "imagica@001" # Placeholder name

# Create a single instance of the settings to be used throughout the application
settings = Settings()
