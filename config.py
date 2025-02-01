from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

import os
import logging
import pika


load_dotenv()


DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITLAB_ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN")

RMQ_HOST = os.environ.get("RMQ_HOST")
RMQ_PORT = os.environ.get("RMQ_PORT")
RMQ_USER = os.environ.get("RMQ_USER")
RMQ_PASSWORD = os.environ.get("RMQ_PASSWORD")
MQ_EXCHANGE = os.environ.get("MQ_EXCHANGE")
MQ_ROUTING_KEY = os.environ.get("MQ_ROUTING_KEY")


class AuthJWT(BaseModel):
    private_key_path: Path = Path("certs") / "jwt-private.pem"
    public_key_path: Path = Path("certs") / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()


class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@localhost:5432/{DB_NAME}'
    db_echo: bool = False

db_settings = DBSettings()


def configure_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )


connection_params = pika.ConnectionParameters(
    host=RMQ_HOST, 
    port=RMQ_PORT,
    # credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD)
)


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(parameters=connection_params)