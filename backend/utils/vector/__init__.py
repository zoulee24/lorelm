import os
from contextlib import asynccontextmanager

from ...schemas import ProfileProvider, ProfileType, SystemProfile
from ._base import VectorDatabase
from ._elastic import ElasticSearch

ES_HOST = os.getenv("ES_HOST", "127.0.0.1")
ES_PORT = int(os.getenv("ES_PORT", "9200"))
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "lorelm")


async def get_vdb():
    profile = SystemProfile(
        name="elasticsearch",
        type=ProfileType.Vector,
        provider=ProfileProvider.ElasticSearch,
        host=ES_HOST,
        port=ES_PORT,
        username=ES_USER,
        password=ES_PASSWORD,
    )
    async with ElasticSearch(profile) as client:
        try:
            yield client
        finally:
            pass


get_vdb_with = asynccontextmanager(get_vdb)
