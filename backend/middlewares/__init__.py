from typing import Final, Tuple

from starlette.middleware.base import BaseHTTPMiddleware

CORS_ORIGINS: Final[Tuple[str, ...]] = ("*",)
CORS_ALLOW_CREDENTIALS: Final[bool] = True
CORS_ALLOW_METHODS: Final[Tuple[str, ...]] = ("*",)
CORS_ALLOW_HEADERS: Final[Tuple[str, ...]] = ("*",)


def make_middlewares():
    from fastapi.middleware import Middleware
    from fastapi.middleware.cors import CORSMiddleware

    return (
        Middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=CORS_ALLOW_CREDENTIALS,
            allow_methods=CORS_ALLOW_METHODS,
            allow_headers=CORS_ALLOW_HEADERS,
        ),
        # Middleware(BaseHTTPMiddleware, dispatch=request_logger),
    )
