from typing import Annotated, NotRequired, Optional, TypedDict, Union

from fastapi import UploadFile
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from ..schemas.base import DataRange, ORMBase


class LabelResponse(ORMBase):
    name: str = Field(max_length=16, description="标签名称")

    model_config = ConfigDict(from_attributes=True)


def _str2list(s: str):
    if isinstance(s, str):
        return s.split(",")
    elif isinstance(s, list):
        if len(s) == 1:
            return s[0].split(",")
        else:
            return s
    else:
        print(f"未处理 str2list 参数错误: {s}")
        return s


def _label_convert(v: str | LabelResponse):
    if isinstance(v, str):
        return v
    elif hasattr(v, "name"):
        return v.name
    else:
        raise TypeError(f"Invalid label type: {type(v)}")


def labels_convert(data: list[str | LabelResponse]):
    if not isinstance(data, (list, tuple)):
        raise TypeError(f"Invalid labels type: {type(data)}")
    return list(map(_label_convert, data))


class WorldResponse(ORMBase):
    """世界响应"""

    nickname: str = Field(description="昵称")
    description: str = Field(default="", description="描述")
    data_range: DataRange = Field(description="数据范围")

    model_config = ConfigDict(from_attributes=True)


class WorldFullResponse(WorldResponse):
    labels: Annotated[list[str], BeforeValidator(labels_convert)] = Field(
        default_factory=list, description="标签"
    )


class WorldCreateForm(BaseModel):
    """世界创建表单"""

    nickname: str = Field(
        min_length=2, max_length=64, description="昵称", examples=["新世界"]
    )
    description: str = Field(
        default="", description="描述", examples=["这是一个奇幻世界"]
    )
    data_range: DataRange = Field(
        DataRange.all, description="数据范围", examples=[DataRange.all, DataRange.self]
    )
    labels: Annotated[list[str], BeforeValidator(_str2list)] = Field(
        default_factory=list, description="标签列表", examples=[["魔法", "中世纪"]]
    )


class CharacterResponse(ORMBase):
    """角色响应"""

    nickname: str = Field(description="昵称")
    avatar: Optional[str] = Field(description="头像")

    description: str = Field(description="描述")
    first_message: str = Field(description="首条信息")
    data_range: DataRange = Field(description="数据范围")

    model_config = ConfigDict(from_attributes=True)


class CharacterFullResponse(CharacterResponse):
    labels: Annotated[list[str], BeforeValidator(labels_convert)] = Field(
        default_factory=list, description="标签"
    )


class CharacterWorldResponse(CharacterFullResponse):
    world: Optional[WorldResponse] = Field(None, description="关联世界")


class CharacterCreateForm(BaseModel):
    """角色响应"""

    nickname: str = Field(min_length=2, max_length=64, description="昵称")
    description: str = Field(description="描述")
    first_message: str = Field(description="首条信息")
    data_range: DataRange = Field(
        DataRange.all, description="数据范围", examples=[DataRange.all, DataRange.self]
    )
    world_id: Optional[int] = Field(None, description="关联世界ID")
    labels: Annotated[list[str], BeforeValidator(_str2list)] = Field(
        default_factory=list, description="标签列表", examples=[["女", "阳光"]]
    )
    avatar: Optional[UploadFile] = Field(None, description="头像")
    files: Union[UploadFile, list[UploadFile]] = Field(
        default_factory=list, description="文件列表"
    )


class DocumentResponse(ORMBase):
    """文档响应"""

    character_id: Optional[int] = Field(description="角色ID")
    content: str = Field(description="内容")
    disabled: bool = Field(False, description="禁用")
    data_range: DataRange = Field(DataRange.self, description="权限")


class DocumentCreateRequest(DocumentResponse):
    """文档创建请求"""

    pass


class DocumentUpdateRequest(DocumentCreateRequest):
    """文档更新请求"""

    pass
