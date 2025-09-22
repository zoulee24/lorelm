import uuid
from typing import Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import BINARY, TIMESTAMP
from sqlalchemy.types import BigInteger as BigIntegerStrict
from sqlalchemy.types import Boolean, Integer, TypeDecorator

T = TypeVar("T")
OptionMapped = Mapped[Optional[T]]

BigInteger = BigIntegerStrict().with_variant(Integer, "sqlite")


class UUIDBinary(TypeDecorator):
    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value.bytes
        elif isinstance(value, str):
            return uuid.UUID(value).bytes
        elif isinstance(value, bytes):
            return uuid.UUID(bytes=value).bytes
        else:
            raise TypeError("Invalid UUID type: %s" % type(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(bytes=value)


class DbBase(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class TableBase(DbBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID",
        sort_order=0,
    )


class ORMBaseSmall(TableBase):
    __abstract__ = True

    created_at: Mapped[float] = mapped_column(
        TIMESTAMP(True), server_default=func.current_timestamp(), comment="创建时间"
    )


class ORMBase(ORMBaseSmall):
    """
    公共 ORM 模型，基表
    """

    __abstract__ = True
    updated_at: Mapped[float] = mapped_column(
        TIMESTAMP(True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="更新时间",
    )
    deleted_at: OptionMapped[float] = mapped_column(
        TIMESTAMP(True), nullable=True, comment="删除时间"
    )
    is_delete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否软删除",
        sort_order=998,
    )
