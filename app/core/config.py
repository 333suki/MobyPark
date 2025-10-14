from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "MobyPark API"
    debug: bool = True

    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'database.db'}"

    class Config:
        env_file = ".env"

settings = Settings()
