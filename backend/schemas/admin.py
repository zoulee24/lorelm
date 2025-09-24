from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PlainValidator

from ..schemas.base import ORMBase


class UserResponse(ORMBase):
    """用户"""

    email: EmailStr = Field(description="邮箱", examples=["<EMAIL>"])
    nickname: str = Field(description="昵称")
    password: str = Field(description="密码")
    avatar: Optional[str] = Field(None, description="头像")
    telephone: Optional[str] = Field(None, description="电话")
    gender: Optional[str] = Field(None, description="性别")
    disabled: bool = Field(False, description="禁用")
    login_at: Optional[datetime] = Field(None, description="登录时间")
    language: str = Field(description="语言")

    model_config = ConfigDict(from_attributes=True)


class UserCreateForm(BaseModel):
    """用户创建表单"""

    email: EmailStr = Field(description="邮箱", examples=["<EMAIL>"])
    nickname: str = Field(
        min_length=1, max_length=32, description="昵称", examples=["loreuser"]
    )
    password: str = Field(min_length=6, description="密码", examples=["123456"])
    avatar: Optional[str] = Field(None, description="头像", examples=[None])
    telephone: Optional[str] = Field(None, description="电话", examples=[None])
    gender: Optional[str] = Field(None, description="性别", examples=[None])
    language: str = Field("简体中文", description="语言")


class UserUpdateRequest(UserCreateForm):
    """用户更新表单"""

    disabled: bool = Field(description="禁用", examples=[False])
