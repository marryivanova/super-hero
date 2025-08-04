from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool
    HOST: str
    PORT: str
    API_HERO: str
    TOKEN: str

    # db
    DB_HOST: str | int
    DB_PORT: str | int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
