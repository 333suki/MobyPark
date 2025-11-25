from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    app_name: str = "MobyPark API"
    debug: bool = True

    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'database.db'}"

settings = Settings()
