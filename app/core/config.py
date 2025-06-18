import os
import secrets
from typing import Literal, Optional
from urllib.parse import quote_plus

class Settings:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()

        self.API_V1_STR = "/api"
        self.SECRET_KEY = secrets.token_urlsafe(32)
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8
        self.DOMAIN = os.getenv("DOMAIN","http://localhost:8000")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

        self.BACKEND_CORS_ORIGINS = [
            "http://localhost:3000",
            "https://fe-shopee-project.onrender.com"
        ]

        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "My Project")
        self.SENTRY_DSN = os.getenv("SENTRY_DSN")

        self.POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
        self.POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB", "database")

    @property
    def server_host(self) -> str:
        if self.ENVIRONMENT == "local":
            return "http://localhost:8000"
        return self.DOMAIN if self.DOMAIN.startswith("http") else f"https://{self.DOMAIN}"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        from urllib.parse import quote_plus
        user = quote_plus(self.POSTGRES_USER)
        pwd = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+psycopg://{user}:{pwd}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()




