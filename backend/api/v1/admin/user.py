import os
from typing import Annotated, Optional

from fastapi import APIRouter, Form, Path, UploadFile

from backend import dependencies
from backend.crud import UserCrud
from backend.dependencies.admin import create_token
from backend.exceptions import CustomException, ErrorCode
from backend.schemas import JwtToken, PageResponse
from backend.schemas import admin as schemas

user_router = APIRouter(prefix="/user")

type PathUserId = Annotated[int, Path(description="用户ID")]
OSS_BUCKET_NAME = "lorelm"


@user_router.get(
    "",
    response_model=PageResponse[schemas.UserResponse],
    dependencies=[dependencies.DependLogin],
)
async def user_list(
    query_params: dependencies.DependPageQuery, db: dependencies.DependSession
):
    crud = UserCrud(db)
    data = await crud.get_datas(query_params.page, query_params.limit)
    total = await crud.get_count()
    return dict(data=data, total=total)


@user_router.get(
    "/info",
    response_model=schemas.UserResponse,
)
async def user_self_info(
    db: dependencies.DependSession,
    user_id: dependencies.DependValidUserId,
):
    data = await UserCrud(db).get_data(user_id, strict=False, scalar=False)
    return data


@user_router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
)
async def user_info(
    db: dependencies.DependSession,
    user_id: PathUserId,
):
    data = await UserCrud(db).get_data(user_id, strict=True, scalar=False)
    return data


@user_router.post(
    "",
    response_model=schemas.UserResponse,
    dependencies=[dependencies.DependLogin],
)
async def user_create(
    form: Annotated[schemas.UserCreateForm, Form()],
    db: dependencies.DependSession,
    oss: dependencies.DependOSS,
    avatar: Annotated[Optional[UploadFile], Form(description="头像")] = None,
):
    crud = UserCrud(db)
    d = form.model_dump()
    d["avatar"] = "/lorelm/resource/default_avatar.webp"
    data = await crud.create_data(d)

    if avatar:
        avatar_url = (
            f"user_{data.id}/avatar.{avatar.filename.rsplit(".", maxsplit=1)[1]}"
        )
        await oss.document_create(
            OSS_BUCKET_NAME,
            avatar_url,
            avatar.file,
            avatar.size,
        )
        avatar_url = f"{OSS_BUCKET_NAME}/{avatar_url}"
        data.avatar = avatar_url
    data = await crud.update_data(data, attribute_names=["updated_at"])
    return data


@user_router.put("/{user_id}", response_model=schemas.UserResponse)
async def user_update(
    form: Annotated[schemas.UserUpdateRequest, Form()],
    db: dependencies.DependSession,
    user_id: PathUserId,
):
    crud = UserCrud(db)
    data = await crud.update_data(form, user_id)
    return data


@user_router.delete("/{user_id}", response_model=None)
async def user_delete(
    db: dependencies.DependSession,
    user_id: PathUserId,
):
    crud = UserCrud(db)
    await crud.delete_data(user_id, strict=True)


async def login(form: dependencies.DependLoginForm, db: dependencies.DependSession):
    user = await UserCrud(db).login(form.username, form.password)
    access_token = create_token(
        {
            "sub": "access_token",
            "user_id": user.id,
            "is_refresh": False,
        }
    )
    refresh_token = create_token(
        {
            "sub": "refresh_token",
            "user_id": user.id,
            "is_refresh": True,
        }
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_token(user: dependencies.DependValidUserId):
    access_token = create_token(
        {
            "sub": "access_token",
            "user_id": user.id,
            "is_refresh": False,
        }
    )
    refresh_token = create_token(
        {
            "sub": "refresh_token",
            "user_id": user.id,
            "is_refresh": True,
        }
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


if (
    isinstance(os.getenv("DEV", "false"), str)
    and os.getenv("DEV", "false").lower() == "true"
):
    from fastapi.responses import ORJSONResponse

    user_router.add_api_route(
        "/dev/login",
        login,
        methods=["POST"],
        response_model=JwtToken,
        response_class=ORJSONResponse,
    )
    user_router.add_api_route(
        "/dev/refresh",
        refresh_token,
        methods=["POST"],
        response_model=JwtToken,
        response_class=ORJSONResponse,
    )

user_router.add_api_route("/login", login, methods=["POST"], response_model=JwtToken)
user_router.add_api_route(
    "/refresh", refresh_token, methods=["POST"], response_model=JwtToken
)
