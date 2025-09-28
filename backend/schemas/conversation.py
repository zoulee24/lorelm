from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from ..schemas.base import ORMBase, ORMBaseSmall
from .character import CharacterResponse, WorldResponse


def characters_convert(data: list[CharacterResponse]):
    if not isinstance(data, list):
        raise TypeError(f"Invalid characters type: {type(data)}")
    return [char.nickname for char in data]


class SessionResponse(ORMBase):
    """会话响应"""

    user_id: int = Field(description="用户ID")
    world_id: Optional[int] = Field(None, description="世界ID")
    act_character_id: Optional[int] = Field(None, description="用户扮演的角色ID")
    title: str = Field(max_length=32, description="会话标题")
    token_usage: int = Field(default=0, description="对话消耗的token数")

    model_config = ConfigDict(from_attributes=True)


class SessionFullResponse(SessionResponse):
    world: Optional[WorldResponse] = Field(description="世界")
    act_character: Optional[CharacterResponse] = Field(description="用户扮演的角色")
    characters: list[CharacterResponse] = Field(
        default_factory=list, description="角色列表"
    )


class SessionMessageResponse(SessionFullResponse):
    messages: list["ConversationHistoryResponse"] = Field(
        default_factory=list, description="会话历史"
    )


class SessionCreateForm(BaseModel):
    """会话创建表单"""

    world_id: Optional[int] = Field(None, description="世界ID", examples=[None, 1])
    act_character_id: Optional[int] = Field(
        None, description="用户扮演的角色ID", examples=[None, 1]
    )
    character_ids: list[int] = Field(
        default_factory=list, description="角色ID列表", examples=[[1]]
    )
    # content: str = Field(min_length=1, description="对话内容", examples=["你好"])
    # title: str = Field(
    #     min_length=1, max_length=32, description="会话标题", examples=["新会话"]
    # )


class SessionUpdateForm(BaseModel):
    """会话更新表单"""

    title: str = Field(min_length=1, max_length=32, description="会话标题")


class ConversationHistoryResponse(ORMBaseSmall):
    """对话历史响应"""

    session_id: int = Field(description="会话ID")
    message_id: str = Field(description="消息ID")
    role: str = Field(description="角色")
    content: Optional[str] = Field(None, description="对话内容")
    reasoning: Optional[str] = Field(None, description="推理过程")
    token_usage: int = Field(default=0, description="对话消耗的token数")

    model_config = ConfigDict(from_attributes=True)


# class ConversationHistoryCreateForm(BaseModel):
#     """对话历史创建表单"""

#     session_id: int = Field(description="会话ID")
#     message_id: str = Field(description="消息ID")
#     role: str = Field(description="角色")
#     content: Optional[str] = Field(None, description="对话内容")
#     reasoning: Optional[str] = Field(None, description="推理过程")
#     token_usage: int = Field(default=0, description="对话消耗的token数")


# class Session2CharacterResponse(TableBase):
#     """会话角色关联响应"""

#     session_id: int = Field(description="会话ID")
#     character_id: int = Field(description="角色ID")
