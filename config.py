from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

import os
import logging
import pika
import time


load_dotenv()


POSTGRES_USER = os.environ.get("POSTGRES_USER", "inksne")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "inksne")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "inksne")

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
    db_url: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}'
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
    while True:
        try:
            connection = pika.BlockingConnection(connection_params)
            print('успех!')
            return connection
        except pika.exceptions.AMQPConnectionError:
            print('повтор')
            time.sleep(5)