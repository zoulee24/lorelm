from typing import Optional

from numpy import ndarray
from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, Index, String, Text, event, func, select
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from ..schemas import DataRange
from .base import BigInteger, ORMBase, TableBase


class Label(ORMBase):
    __tablename__ = "label"
    __table_args__ = {
        "comment": "角色标签表",
    }
    name: Mapped[str] = mapped_column(String(16), nullable=False, comment="标签名称")

    # characters: Mapped[list["Character"]] = relationship(
    #     secondary="m2m_label_character", uselist=True
    # )


class World(ORMBase):
    __tablename__ = "world"
    __table_args__ = {"comment": "世界表"}

    nickname: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="昵称"
    )
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")

    labels: Mapped[list["Label"]] = relationship(
        secondary="m2m_label_world", uselist=True
    )
    characters: Mapped[list["Character"]] = relationship(
        secondary="m2m_world_character", uselist=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id"),
        index=True,
        comment="用户ID",
    )
    data_range: Mapped[str] = mapped_column(
        String(16), default=DataRange.all, comment="数据范围"
    )


class Character(ORMBase):
    __tablename__ = "character"
    __table_args__ = (
        Index(
            "ix_nickname_gin",
            "nickname",
            postgresql_using="gin",
            postgresql_ops={"nickname": "gin_trgm_ops"},
        ),
        {"comment": "角色表"},
    )
    avatar: Mapped[str] = mapped_column(String(128), nullable=True, comment="头像")
    nickname: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="昵称"
    )
    description: Mapped[str] = mapped_column(Text, comment="描述")
    first_message: Mapped[str] = mapped_column(Text, comment="首条信息")

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id"),
        index=True,
        comment="用户ID",
    )
    world_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("world.id"),
        index=True,
        nullable=True,
        comment="世界ID",
    )
    data_range: Mapped[str] = mapped_column(
        String(16), default=DataRange.all, comment="数据范围"
    )

    labels: Mapped[list["Label"]] = relationship(
        secondary="m2m_label_character", uselist=True
    )


class Document(ORMBase):
    __tablename__ = "document"
    __table_args__ = (
        # 向量索引
        Index("ix_content_ltks_gin", "content_ltks_tsvector", postgresql_using="gin"),
        Index(
            "ix_content_sm_ltks_gin", "content_sm_ltks_tsvector", postgresql_using="gin"
        ),
        Index(
            "ix_vector_cosine",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
        ),
        {"comment": "文档表"},
    )

    character_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("character.id"),
        nullable=True,
        comment="角色ID",
        index=True,
    )
    world_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("world.id"),
        nullable=True,
        comment="世界ID",
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, comment="内容")

    content_ltks: Mapped[str] = mapped_column(Text, comment="内容粗分词")
    content_sm_ltks: Mapped[str] = mapped_column(Text, comment="内容细分词")
    content_ltks_tsvector: Mapped[str] = mapped_column(TSVECTOR, comment="内容粗分词")
    content_sm_ltks_tsvector: Mapped[str] = mapped_column(
        TSVECTOR, comment="内容细分词"
    )

    embedding: Mapped[ndarray] = mapped_column(Vector(1024), comment="嵌入")

    disabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否禁用", index=True
    )
    data_range: Mapped[str] = mapped_column(
        String(16), default=DataRange.all, comment="数据范围"
    )


def generate_tsvector(mapper, connection, target):
    session = Session.object_session(target)
    if session is None:
        return None
    field_mapping = {
        "title_tks": "title_tks_tsvector",
        "title_sm_tks": "title_sm_tks_tsvector",
        "content_ltks": "content_ltks_tsvector",
        "content_sm_ltks": "content_sm_ltks_tsvector",
    }
    for text_field, tsvector_field in field_mapping.items():
        text_value = getattr(target, text_field) or ""
        # 使用 PostgreSQL 的 to_tsvector('simple', ...)
        # 'simple' 词典 = 按空格分词，无停用词过滤（对应你 ES 的 whitespace analyzer）
        vector_expr = func.to_tsvector("simple", text_value)

        # 执行查询获取 tsvector 字符串（如：'合同':1 '签署':2）
        # 注意：必须用标量查询，因为 func.to_tsvector 返回的是 SQL 表达式
        result = session.scalar(select(vector_expr))
        setattr(target, tsvector_field, result)


class Lable2World(TableBase):
    __tablename__ = "m2m_label_world"
    __table_args__ = {"comment": "标签世界关联表"}

    label_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("label.id", ondelete="CASCADE"), index=True
    )
    world_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("world.id", ondelete="CASCADE"), index=True
    )


class World2Character(TableBase):
    __tablename__ = "m2m_world_character"
    __table_args__ = {"comment": "世界角色关联表"}

    world_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("world.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("character.id", ondelete="CASCADE"), index=True
    )


class Lable2Character(TableBase):
    __tablename__ = "m2m_label_character"
    __table_args__ = {"comment": "标签角色关联表"}

    label_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("label.id", ondelete="CASCADE"), index=True
    )
    character_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("character.id", ondelete="CASCADE"), index=True
    )


event.listens_for(Document, "before_update")(generate_tsvector)
event.listens_for(Document, "before_insert")(generate_tsvector)
