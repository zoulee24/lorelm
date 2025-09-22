from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

from ..schemas.base import DataRange, ORMBase, TableBase


class LabelResponse(ORMBase):
    name: str = Field(max_length=16, description="标签名称")


def _label_convert(v: str | LabelResponse):
    if isinstance(v, LabelResponse):
        return v.name
    elif isinstance(v, str):
        return v
    else:
        raise TypeError(f"Invalid label type: {type(v)}")


def labels_convert(data: list[str | LabelResponse]):
    if not isinstance(data, (list, tuple)):
        raise TypeError(f"Invalid labels type: {type(data)}")
    return list(map(_label_convert, data))


class CharacterResponse(ORMBase):
    """角色响应"""

    nickname: str = Field(description="昵称")
    labels: Annotated[list[str], BeforeValidator(labels_convert)] = Field(
        default_factory=list, description="标签"
    )

    description: str = Field(description="描述")
    first_message: str = Field(description="首条信息")
    data_range: DataRange = Field(description="数据范围")


def str2list(s: str):
    if isinstance(s, str):
        return s.split(",")
    elif isinstance(s, list) and len(s) == 1:
        return s[0].split(",")
    else:
        print(f"未处理 str2list 参数错误: {s}")
        return s


class CharacterCreateForm(BaseModel):
    """角色响应"""

    nickname: str = Field(min_length=2, max_length=64, description="昵称")
    description: str = Field(description="描述")
    first_message: str = Field(description="首条信息")
    data_range: DataRange = Field(
        DataRange.all, description="数据范围", examples=[DataRange.all, DataRange.self]
    )
    labels: Annotated[list[str], BeforeValidator(str2list)] = Field(
        default_factory=list, description="标签列表", examples=[["女", "阳光"]]
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
