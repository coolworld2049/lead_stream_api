import socket
from contextlib import closing

from loguru import logger
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel

from app.settings import settings

engine = create_engine(
    settings.db_url,
    echo=settings.SQLALCHEMY_ECHO,
)


def on_database_startup():
    SQLModel.metadata.create_all(engine)
    logger.info("SQLModel metadata created")


def on_database_shutdown():
    engine.dispose()


def check_socket(host, port, timeout):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False


sql_session_factory = sessionmaker(engine, autoflush=False)
