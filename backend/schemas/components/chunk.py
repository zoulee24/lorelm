from typing import NotRequired, Optional, TypedDict

from numpy import ndarray
from pydantic import BaseModel, ConfigDict


class DocumentCreateDict(TypedDict, total=False):
    doc_id: int

    content: str
    content_ltks: str
    content_sm_ltks: str
    vector: list[float]

    create_at: int
    update_at: int
    delete_at: Optional[int]


class DocumentDict(TypedDict):
    id: str

    doc_id: int

    create_at: int
    update_at: int
    delete_at: Optional[int]

    method: str

    content: str


class ChunkingConfig(BaseModel):
    chunk_size: int
    overlap_size: int
    embed_tag: str

    model_config = ConfigDict(from_attributes=True)
