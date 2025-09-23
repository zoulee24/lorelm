from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import AliasChoices, AliasPath, BaseModel, Field, NonNegativeInt


class DbBase(BaseModel):
    pass


class TableBase(DbBase):
    id: NonNegativeInt = Field(description="主键ID")


class ORMBaseSmall(TableBase):
    created_at: datetime = Field(description="创建时间")


class ORMBase(ORMBaseSmall):
    # deleted_at: Optional[datetime] = Field(description="删除时间")
    # is_delete: bool = Field(False, description="是否软删除")
    updated_at: datetime = Field(description="更新时间")


class PageResponse[T](BaseModel):
    data: list[T] = Field(description="数据")
    total: NonNegativeInt = Field(description="总条数")


class DataRange(StrEnum):
    """数据权限范围"""

    all = "all"
    self = "self"
    custom = "custom"


class JwtToken(BaseModel):
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(description="令牌类型")
