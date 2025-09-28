import os
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from backend.exceptions.handler import register_exceptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .dependencies.database import db_deinit, db_init

    # before fastapi start
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8888))
    logger = getLogger("omni-rag")

    logger.info("before fastapi start")

    logger.info("backend init begin")
    await db_init()
    logger.info("backend init finished")

    logger.info(f"Fastapi Doc address: http://{host}:{port}{app.docs_url}")

    try:
        yield
    finally:
        # after fastapi stop
        logger.info("after fastapi stop")
        await db_deinit()
        logger.info("backend deinit finished")


def create_app():
    from logging import StreamHandler

    from coloredlogs import ColoredFormatter as _ColoredFormatter

    from .api import api_router
    from .middlewares import make_middlewares

    _handler = StreamHandler()
    _handler.setFormatter(
        _ColoredFormatter(
            "%(asctime)s [%(process)d] [%(levelname)s] %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    _logger = getLogger("lorelm")
    _logger.addHandler(_handler)
    _logger.setLevel(20)

    app = FastAPI(lifespan=lifespan, middleware=make_middlewares())
    app.include_router(api_router)
    register_exceptions(app)
    return app
