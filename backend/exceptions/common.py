from enum import Enum
from typing import Optional, Union

# from backend.schemas.profile import ProfileType


class ErrorCode(Enum):
    OK = (0, 0, "成功")

    Other = (1, 0, "其他错误")

    NotExist = (1, 1, "不存在")
    Exist = (1, 2, "已存在")
    Repeat = (1, 3, "重复")
    Params = (1, 4, "参数错误")

    UnLogin = (2, 0, "未登录")
    TokenVerify = (2, 1, "Token错误")
    TokenExpired = (2, 2, "Token已过期")
    Permission = (2, 3, "权限不足")
    Authorized = (2, 4, "需要授权")
    UserOrPassword = (2, 5, "用户名或密码错误")

    def __init__(self, namespace: int, code: int, msg: str):
        self.code = 10000 + namespace * 1000 + code
        self.msg = msg


class CustomException(Exception):
    def __init__(self, code: Union[int, ErrorCode], msg: Optional[str] = None):
        if isinstance(code, ErrorCode):
            self.code = code.code
            self.msg = msg if msg else code.msg
        elif isinstance(code, int) and msg is not None:
            self.code = code
            self.msg = msg
        else:
            raise ValueError("msg 不能为空")


# class ToolNotConfigured(Exception):
#     def __init__(self, tool_type: ProfileType):
#         self.tool_type = tool_type
#         super().__init__(f"{tool_type} 未配置")
