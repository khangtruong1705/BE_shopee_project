from dotenv import load_dotenv
import os
import secrets
from typing import ClassVar
from typing import Any, Literal
from pydantic import (
    HttpUrl,
    PostgresDsn,
    computed_field
)

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "https://be-shopee-project.onrender.com"
    ENVIRONMENT: Literal["local", "staging", "production"] = "production"

    @computed_field 
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://localhost:8000"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://fe-shopee-project.onrender.com"
    ]
    

    PROJECT_NAME:ClassVar[str] = os.getenv("PROJECT_NAME")
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER:ClassVar[str] = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT:ClassVar[int] = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_USER:ClassVar[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD:ClassVar[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB:ClassVar[str]= os.getenv("POSTGRES_DB")

    # PROJECT_NAME: str = 'e-commerce'
    # SENTRY_DSN: HttpUrl | None = None
    # POSTGRES_SERVER: str = "localhost"
    # POSTGRES_PORT: int = 5432  
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "postgres"
    # POSTGRES_DB: str = "shopeeDB"
    @computed_field  
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )



settings = Settings() 
