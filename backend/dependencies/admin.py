from typing import Annotated, Final, List, Optional, TypedDict, Union
from uuid import uuid4

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..crud import UserCrud
from ..dependencies.database import DependSession
from ..exceptions import CustomException, ErrorCode
from ..utils import get_unix_timestamp

ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
JWT_SECRET_KEY: Final[str] = "secret"
JWT_ALGORITHMS: Final[str] = "HS256"
TOKEN_ENDPOINT: Final[str] = "/api/v1/admin/user/dev/login"
REFRESH_TOKEN_ENDPOINT: Final[str] = "/api/v1/admin/user/dev/refresh"


class JWTPayload(TypedDict, total=False):
    """JWT (JSON Web Token) 的标准载荷字段定义。

    各字段含义参考 RFC 7519 标准。
    """

    iss: str
    """issuer (签发者)：标识签发JWT的主体"""

    sub: str
    """subject (主题)：标识JWT的主题"""

    exp: int
    """expiration time (过期时间)：JWT的过期时间，必须是Unix时间戳（整数）"""

    aud: Union[str, List[str]]
    """audience (受众)：标识JWT的预期接收者，可以是字符串或字符串数组"""

    iat: int
    """issued at (签发时间)：JWT的签发时间，必须是Unix时间戳（整数）"""

    jti: str
    """JWT ID (唯一标识)：为JWT提供唯一标识"""


class CustomJWTPayload(JWTPayload):
    is_refresh: bool

    user_id: int


_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=TOKEN_ENDPOINT, refreshUrl=REFRESH_TOKEN_ENDPOINT, auto_error=False
)


def create_token(payload: CustomJWTPayload, expires: Optional[int] = None):
    global ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY, JWT_ALGORITHMS
    now = get_unix_timestamp()
    if expires:
        expire = now + expires * 60
    else:
        expire = now + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    payload.update(
        {
            "iss": "modern-fastapi-backend",
            "exp": expire,
            # "iat": now,
            "jti": str(uuid4()),
        }
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHMS)


def get_jwt_payload(token: Annotated[Optional[str], Depends(_oauth2_scheme)]):
    if token is None:
        return None
    try:
        payload: CustomJWTPayload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=(JWT_ALGORITHMS,)
        )
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise CustomException(ErrorCode.TokenVerify)
    except (
        jwt.exceptions.ExpiredSignatureError,
        jwt.exceptions.ImmatureSignatureError,
    ):
        raise CustomException(ErrorCode.TokenExpired)
    return payload


async def get_user_id_open(
    payload: Annotated[Optional[CustomJWTPayload], Depends(get_jwt_payload)],
):
    if payload is None:
        return None
    return payload.get("user_id", None)


async def get_user_id(
    user_id: Annotated[Optional[int], Depends(get_user_id_open)],
):
    if user_id is None:
        raise CustomException(ErrorCode.Authorized)
    return user_id


async def get_valid_user_id(
    user_id: Annotated[int, Depends(get_user_id)], db: DependSession
):
    user_crud = UserCrud(db)
    return await user_crud.get_id(user_id)


async def get_user(
    user_id: Annotated[CustomJWTPayload, Depends(get_user_id)],
    db: DependSession,
):
    user_crud = UserCrud(db)
    user = await user_crud.get_data(user_id)
    if user is None:
        raise CustomException(ErrorCode.NotExist)
    return user


async def get_refresh_token(
    payload: Annotated[Optional[CustomJWTPayload], Depends(get_jwt_payload)],
) -> CustomJWTPayload:
    if payload is None:
        raise CustomException(ErrorCode.Authorized)
    is_refresh = payload.get("is_refresh", False)
    if not isinstance(is_refresh, bool):
        raise CustomException(ErrorCode.TokenVerify)
    elif not is_refresh:
        raise CustomException(ErrorCode.TokenVerify)
    return payload


DependLogin = Depends(get_valid_user_id)
DependRefreshToken = Depends(get_refresh_token)
DependLoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]
DependOptionalUserId = Annotated[Optional[int], Depends(get_user_id_open)]
DependValidUserId = Annotated[int, DependLogin]
# DependUser = Annotated[schemas.UserResponse, Depends(get_user)]
