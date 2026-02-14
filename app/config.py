from pydantic_settings import BaseSettings
from pydantic import ConfigDict

from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Analysis & AI
    GOOGLE_API_KEY: str = ""
    ANALYSIS_TIMEOUT: int = 10
    ENABLE_RATE_LIMIT: bool = True

    model_config = ConfigDict(env_file=".env")

settings = Settings()
