import asyncio
import os
from typing import Literal, Optional

from ...schemas.components.chunk import DocumentCreateDict

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")
OPENAI_EMBED_DIMS = int(os.getenv("OPENAI_EMBED_DIMS"))
assert OPENAI_EMBED_DIMS == 1024, "OPENAI_EMBED_DIMS must be 1024"


async def chunking(
    method: Literal["naive"],
    content: str,
    role_id: Optional[int],
    world_id: Optional[int],
):
    match method:
        case "naive":
            docs = await naive_chunk(content, role_id, world_id)
        case _:
            raise ValueError(f"Unknown chunk method: {method}")
    return docs


async def naive_chunk(content: str, role_id: Optional[int], world_id: Optional[int]):
    from omni_llm import async_embedding_factory

    from ...schemas.components import ChunkingConfig
    from .naive import ChunkingNaive

    embed_md = async_embedding_factory("siliconflow")(
        OPENAI_EMBED_MODEL,
        -1,
        OPENAI_EMBED_DIMS,
        OPENAI_BASE_URL,
        OPENAI_API_KEY,
    )
    chunk_config = ChunkingConfig(
        chunk_size=128, overlap_size=0, embed_tag=OPENAI_EMBED_MODEL
    )

    docs = await asyncio.to_thread(ChunkingNaive(chunk_config.model_dump()), content)
    content_vectors = (await embed_md.encode(list(doc["content"] for doc in docs))).v

    for doc, content_vector in zip(docs, content_vectors):
        doc["vector"] = content_vector
        doc["role_id"] = role_id
        doc["world_id"] = world_id
    return docs
