import os
from operator import attrgetter
from typing import Annotated, Optional, Union

from fastapi import APIRouter, Body, Form, Path, Query, UploadFile
from fastapi.responses import StreamingResponse
from omni_llm import ChatOutput, async_chat_factory
from sqlalchemy import or_, select

from backend import dependencies
from backend.crud import CharacterCrud, LabelCrud, UserCrud, WorldCrud
from backend.exceptions import CustomException, ErrorCode
from backend.prompts import get_prompt_template
from backend.schemas import PageResponse
from backend.schemas import character as schemas

role_router = APIRouter(prefix="/character", tags=["角色"])
world_router = APIRouter(prefix="/world", tags=["世界"])
label_router = APIRouter(prefix="/label", tags=["标签"])

PathRoleId = Annotated[int, Path(description="角色ID")]
PathLabelId = Annotated[int, Path(description="标签ID")]
PathWorldId = Annotated[int, Path(description="世界ID")]

OSS_BUCKET_NAME = "lorelm"


@role_router.get(
    "", response_model=PageResponse[schemas.CharacterResponse], summary="角色列表"
)
async def role_list(
    query_params: dependencies.DependPageQuery, db: dependencies.DependSession
):
    crud = CharacterCrud(db)
    data = await crud.get_datas(query_params.page, query_params.limit)
    total = await crud.get_count()
    return dict(data=data, total=total)


@role_router.get(
    "/{role_id}", response_model=schemas.CharacterResponse, summary="角色信息"
)
async def role_info(role_id: PathRoleId, db: dependencies.DependSession):
    crud = CharacterCrud(db)
    data = await crud.get_data(role_id, strict=True, scalar=False)
    return data


@role_router.post("", response_model=schemas.CharacterResponse)
async def role_info(
    form: Annotated[
        schemas.CharacterCreateForm, Form(media_type="multipart/form-data")
    ],
    user_id: dependencies.DependValidUserId,
    db: dependencies.DependSession,
    oss: dependencies.DependOSS,
):
    if not isinstance(form.files, list):
        form.files = [form.files]
    crud = CharacterCrud(db)
    data = await crud.create_data(form, user_id)

    if form.avatar:
        avatar_url = (
            f"role_{data.id}/avatar.{form.avatar.filename.rsplit(".", maxsplit=1)[1]}"
        )
        await oss.document_create(
            OSS_BUCKET_NAME,
            avatar_url,
            form.avatar.file,
            form.avatar.size,
        )
        avatar_url = f"/{OSS_BUCKET_NAME}/{avatar_url}"
        data.avatar = avatar_url

    # for file in files:
    #     file_path = f"role_{data.id}/{file.filename}"
    #     assert await oss.document_create(
    #         OSS_BUCKET_NAME, file_path, file.file, file.size
    #     ), "上传失败"

    # TODO 构建知识库

    return data


@world_router.get(
    "",
    response_model=PageResponse[schemas.WorldFullResponse],
    summary="世界列表",
)
async def world_list(
    query_params: dependencies.DependPageQuery, db: dependencies.DependSession
):
    crud = WorldCrud(db)
    data = await crud.get_datas(query_params.page, query_params.limit)
    total = await crud.get_count()
    return dict(data=data, total=total)


@world_router.get("/stream", response_model=list[schemas.LabelResponse])
async def world_stream(
    name: Annotated[str, Query(max_length=16, description="")],
    db: dependencies.DependSession,
):
    crud = WorldCrud(db)
    result = await crud.execute(
        select(
            crud.model.nickname.label("name"),
            crud.model.id,
            crud.model.created_at,
            crud.model.updated_at,
        ).where(
            or_(
                crud.model.nickname.like(f"%{name}%"),
                crud.model.description.like(f"%{name}%"),
            )
        )
    )
    return result.all()


@world_router.get(
    "/{world_id}", response_model=schemas.WorldFullResponse, summary="世界信息"
)
async def world_info(world_id: PathWorldId, db: dependencies.DependSession):
    crud = WorldCrud(db)
    data = await crud.get_data(world_id, strict=True, scalar=False)
    return data


@world_router.get(
    "/{world_id}/characters",
    response_model=list[schemas.CharacterResponse],
    summary="世界关联角色",
)
async def world_info(world_id: PathWorldId, db: dependencies.DependSession):
    crud = CharacterCrud(db)
    data = await crud.get_datas(wheres=crud.model.world_id == world_id)
    return data


@world_router.post("", response_model=schemas.WorldFullResponse, summary="创建世界")
async def world_create(
    form: Annotated[schemas.WorldCreateForm, Form()],
    user_id: dependencies.DependValidUserId,
    db: dependencies.DependSession,
):
    crud = WorldCrud(db)
    data = await crud.create_data(form, user_id)
    return data


@label_router.get("/", response_model=PageResponse[schemas.LabelResponse])
async def label_list(
    query_params: dependencies.DependPageQuery, db: dependencies.DependSession
):
    crud = LabelCrud(db)
    wheres = (
        None
        if query_params.search is None
        else crud.model.name.like(f"%{query_params.search}%")
    )
    data = await crud.get_datas(query_params.page, query_params.limit, wheres=wheres)
    total = await crud.get_count()
    return dict(data=data, total=total)


@label_router.get("/stream", response_model=list[schemas.LabelResponse])
async def label_list(
    name: Annotated[str, Query(max_length=16, description="")],
    db: dependencies.DependSession,
):
    crud = LabelCrud(db)
    data = await crud.get_datas(1, 10, wheres=crud.model.name.like(f"%{name}%"))
    return data


@label_router.post("/", summary="创建标签", response_model=list[schemas.LabelResponse])
async def label_create(
    data: Annotated[list[str], Body(description="标签")],
    db: dependencies.DependSession,
):
    crud = LabelCrud(db)
    exist_label_model = await crud.get_datas(
        wheres=crud.model.name.in_(data.labels),
        scalar=False,
    )
    not_exist_labels = set(data.labels) - set(
        map(attrgetter("name"), exist_label_model)
    )
    if not not_exist_labels:
        return []
    not_exist_label_models = await crud.batch_create(not_exist_labels)
    return not_exist_label_models


@label_router.delete("/{label_id}", summary="删除标签")
async def label_delete(label_id: PathLabelId, db: dependencies.DependSession):
    crud = LabelCrud(db)
    await crud.delete_data(label_id)
