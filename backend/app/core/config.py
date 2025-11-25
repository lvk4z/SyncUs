from pydantic_settings import BaseSettings

class Settings(BaseSettings): 
    PROJECT_NAME: str = "SyncUs"
    DATABASE_URL: str
    SECRET_KEY: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    class Config:
        env_file = ".env"

settings = Settings()