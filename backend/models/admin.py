from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP, Boolean, String

from .base import BigInteger, OptionMapped, ORMBase, TableBase


class User(ORMBase):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}

    email: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="邮箱"
    )
    nickname: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False, comment="昵称"
    )
    password: Mapped[str] = mapped_column(String(255), comment="密码")

    avatar: OptionMapped[str] = mapped_column(
        String(128), nullable=True, comment="头像"
    )
    telephone: OptionMapped[str] = mapped_column(
        String(14), nullable=True, index=True, comment="手机号"
    )
    gender: Mapped[str] = mapped_column(String(8), default="男", comment="性别")
    disabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否禁用", index=True
    )
    login_at: OptionMapped[datetime] = mapped_column(
        TIMESTAMP(True), nullable=True, comment="登录时间"
    )
    language: Mapped[str] = mapped_column(
        String(16), default="简体中文", comment="语言"
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否管理员")
