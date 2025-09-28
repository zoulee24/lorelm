import os
from contextlib import asynccontextmanager

from ...schemas import ProfileProvider, ProfileType, SystemProfile
from ._base import ObjectStoreServiceBase
from .minio import Minio

MINIO_HOST = os.getenv("MINIO_HOST", "127.0.0.1")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_USER = os.getenv("MINIO_USER", "lorelm")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD", "lorelm123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


async def get_oss():
    profile = SystemProfile(
        name="minio",
        type=ProfileType.OSS,
        provider=ProfileProvider.Minio,
        host=MINIO_HOST,
        port=int(MINIO_PORT),
        username=MINIO_USER,
        password=MINIO_PASSWORD,
        db=None,
        extra={"secure": MINIO_SECURE},
    )
    async with Minio(profile) as client:
        try:
            yield client
        finally:
            pass


get_oss_with = asynccontextmanager(get_oss)
