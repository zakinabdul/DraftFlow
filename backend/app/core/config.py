from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Required fields
    APP_NAME: str
    API_V1_STR: str
    DATABASE_URL: str
    GROQ_API: str
    # Fields with defaults
    DEBUG: bool = False 

    model_config = SettingsConfigDict(
        # 1. Where to look for the file locally
        env_file=[".env", "envs/.env.prod", "envs/.env"],
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()