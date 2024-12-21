from pydantic import BaseSettings

class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    DATABASE_URL: str
    SOCIAL_GOOGLE_CLIENT_ID: str
    SOCIAL_GOOGLE_CLIENT_SECRET: str
    SOCIAL_GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    SOCIAL_GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"

    class Config:
        env_file = ".env"

settings = AuthSettings()
