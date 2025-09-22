from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Boolean, TIMESTAMP

from .base import BigInteger, ORMBase, TableBase, OptionMapped


class User(ORMBase):
    __tablename__ = "user"
    __table_args__ = {"comment": "用户表"}

    nickname: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False, comment="昵称"
    )
    password: Mapped[str] = mapped_column(String(255), comment="密码")

    avatar: OptionMapped[str] = mapped_column(
        String(128), nullable=True, comment="头像"
    )
    telephone: OptionMapped[str] = mapped_column(
        String(14), index=True, comment="手机号"
    )
    gender: OptionMapped[str] = mapped_column(String(8), nullable=True, comment="性别")
    disabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否禁用", index=True
    )
    login_at: OptionMapped[datetime] = mapped_column(
        TIMESTAMP(True), nullable=True, comment="登录时间"
    )
