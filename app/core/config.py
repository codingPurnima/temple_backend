from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str= "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int= 30
    REFRESH_TOKEN_EXPIRE_DAYS: int= 14
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    SUPER_ADMIN_PASSWORD: str
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_NAME: str
    class Config:
        env_file= ".env"

settings= Settings()