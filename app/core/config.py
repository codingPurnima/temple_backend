from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str= "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int= 30
    REFRESH_TOKEN_EXPIRE_DAYS: int= 14
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str

    class Config:
        env_file= ".env"

settings= Settings()