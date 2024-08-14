import pathlib

from dotenv import load_dotenv
from prisma import Prisma
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=pathlib.Path(__file__).parent.parent.joinpath(".env"))


class Settings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    IS_DEBUG: bool = False

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    API_KEYS: list[str]
    SECURE_PATH: str

    LEADCRAFT_API_URL: str
    LEADCRAFT_API_KEY: str

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="allow")

    @property
    def db_url(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    @field_validator(
        "API_KEYS",
    )
    def validate_api_keys(cls, api_keys):
        min_length = 32
        for key in api_keys:
            if len(key) < min_length:
                raise ValueError(
                    f"API key '{key}' is shorter than the minimum length of {min_length} characters."
                )
        return api_keys


settings = Settings()
prisma = Prisma()
