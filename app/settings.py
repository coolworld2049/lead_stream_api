import pathlib

from dotenv import load_dotenv
from prisma import Prisma
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=pathlib.Path(__file__).parent.parent.joinpath(".env"))


class Settings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_DB_POOL_SIZE: int = 100
    SQLALCHEMY_WEB_CONCURRENCY: int = 2

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    DATABASE_URL: str

    @property
    def db_url(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="allow")


settings = Settings()
prisma = Prisma()
