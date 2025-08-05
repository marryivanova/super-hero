from urllib.parse import quote_plus

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

    @property
    def DB_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = [".env", "../.env", "../../.env"]
        env_file_encoding = "utf-8"


settings = Settings()
