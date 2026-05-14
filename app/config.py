from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "DentAI - Oral Pathology Education"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./dentist_cv.db"
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE_MB: int = 20
    CV_MODEL_PATH: str = "cv/saved_model"
    CONFIDENCE_THRESHOLD: float = 0.6

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
