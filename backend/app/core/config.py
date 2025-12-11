from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Required fields
    APP_NAME: str
    API_V1_STR: str
    DATABASE_URL: str
    
    # Fields with defaults
    DEBUG: bool = False 

    model_config = SettingsConfigDict(
        # 1. Where to look for the file locally
        env_file=[".env", "envs/.env.prod", "envs/.env"], 
        
        env_ignore_missing=True, 
        
        env_file_encoding='utf-8',
        
        # If there are extra variables in the env file not listed above, ignore them
        extra="ignore"
    )

settings = Settings()