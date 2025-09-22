from typing import Annotated, Optional

from fastapi import Query
from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt


class QueryModel(BaseModel):
    page: PositiveInt = Field(1, description="当前页码", example=1)
    limit: NonNegativeInt = Field(0, description="每页数量", example=10)
    search: Optional[str] = Field(None, description="搜索关键字")


DependPageQuery = Annotated[QueryModel, Query(description="分页参数")]
