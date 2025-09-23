from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BigInteger, ORMBase, TableBase
from .character import Character


class ConversationSession(ORMBase):
    __tablename__ = "conversation_session"
    __table_args__ = {"comment": "大语言模型对话会话"}

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id"),
        index=True,
        comment="用户ID",
    )
    world_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("world.id"),
        nullable=True,
        index=True,
        comment="世界ID",
    )
    act_character_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("character.id"),
        nullable=True,
        index=True,
        comment="用户扮演的角色ID",
    )

    title: Mapped[str] = mapped_column(String(32), comment="会话标题")

    token_usage: Mapped[int] = mapped_column(
        Integer, default=0, comment="对话消耗的token数"
    )

    characters: Mapped[list["Character"]] = relationship(
        secondary="m2m_session_character", uselist=True
    )
    messages: Mapped[list["ConversationHistory"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=True
    )


class ConversationHistory(ORMBase):
    __tablename__ = "conversation_history"
    __table_args__ = {"comment": "大语言模型对话历史"}

    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("conversation_session.id", ondelete="CASCADE"),
        comment="会话ID",
    )
    message_id: Mapped[str] = mapped_column(String(36), comment="消息ID")
    # parent_id: Mapped[Optional[int]] = mapped_column(
    #     BigInteger,
    #     ForeignKey("conversation_history.id", ondelete="CASCADE"),
    #     nullable=True,
    #     comment="父对话历史ID",
    # )
    role: Mapped[str] = mapped_column(
        String(16),
        comment="角色",
    )
    content: Mapped[str] = mapped_column(Text, nullable=True, comment="对话内容")
    reasoning: Mapped[str] = mapped_column(Text, nullable=True, comment="推理过程")
    token_usage: Mapped[int] = mapped_column(
        Integer, default=0, comment="对话消耗的token数"
    )

    session: Mapped[ConversationSession] = relationship(back_populates="messages")


class Session2Character(TableBase):
    __tablename__ = "m2m_session_character"
    __table_args__ = {"comment": "角色会话关联表"}

    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("conversation_session.id", ondelete="CASCADE"),
        index=True,
    )
    character_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("character.id", ondelete="CASCADE"), index=True
    )
