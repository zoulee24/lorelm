from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ..schemas.base import ORMBase


class UserResponse(ORMBase):
    """用户"""

    nickname: str = Field(description="昵称")
    password: str = Field(description="密码")
    avatar: Optional[str] = Field(None, description="头像")
    telephone: Optional[str] = Field(None, description="电话")
    gender: Optional[str] = Field(None, description="性别")
    disabled: bool = Field(False, description="禁用")
    login_at: Optional[datetime] = Field(None, description="登录时间")

    model_config = ConfigDict(from_attributes=True)


class UserCreateForm(BaseModel):
    """用户创建表单"""

    nickname: str = Field(
        ..., min_length=1, max_length=32, description="昵称", examples=["loreuser"]
    )
    password: str = Field(..., min_length=6, description="密码", examples=["123456"])
    avatar: Optional[str] = Field(None, description="头像", examples=[None])
    telephone: Optional[str] = Field(None, description="电话", examples=[None])
    gender: Optional[str] = Field(None, description="性别", examples=[None])


class UserUpdateRequest(UserCreateForm):
    """用户更新表单"""

    disabled: bool = Field(description="禁用", examples=[False])
