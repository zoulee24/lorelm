import os
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Annotated, AsyncGenerator, Final

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

db_name = os.getenv("POSTGRES_DB", "lorelm")
user = os.getenv("POSTGRES_USER", "lorelm")
password = os.getenv("POSTGRES_PASSWORD", "lorelm123")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", 5432)

DATABASE_URL: Final[str] = (
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"
)
logger = getLogger("lorelm.db")
_engine = None
session_factory = None


async def db_init(app: FastAPI):
    global _engine, session_factory, logger
    from ..models import DbBase

    _engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        echo_pool=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=5,
        connect_args={},
    )
    session_factory = async_sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=True,
        class_=AsyncSession,
    )

    logger.info(f"init finished")


async def db_deinit(app: FastAPI):
    global _engine, session_factory, logger

    _engine = None
    session_factory = None
    logger.info(f"deinit finished")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        async with session.begin():
            try:
                yield session
            finally:
                # await session.close()
                pass


DependSession = Annotated[AsyncSession, Depends(get_session)]
get_session_with = asynccontextmanager(get_session)
