
"""
Central app configuration.
Reads values from a .env file at project root (same level as main.py).
Install: pip install pydantic-settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "sqlite:///./globetrotter.db"  # swap for postgres in prod

    # --- JWT / Auth ---
    SECRET_KEY: str = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"  # override via .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day, good enough for hackathon

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()