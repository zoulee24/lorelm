import os
from operator import attrgetter
from typing import Annotated

from fastapi import APIRouter, Body, Form, Path, Query
from fastapi.responses import StreamingResponse
from omni_llm import ChatOutput, async_chat_factory

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


async def create_chat(
    role_id: int,
    content: str,
    user_id: int,
):
    async with dependencies.get_session_with() as db:
        crud = CharacterCrud(db)
        user_crud = UserCrud(db)
        role = await crud.get_data(role_id, strict=True, scalar=False)
        user = await user_crud.get_data(user_id, strict=True, scalar=False)

        task_prompt = get_prompt_template("task").render(
            role=role, user=user, language="简体中文"
        )
        policy_prompt = get_prompt_template("policy").render(
            role=role, user=user, jailbreak=True, policy=True, language="简体中文"
        )
        info_prompt = get_prompt_template("info").render(
            role=role, user=user, language="简体中文"
        )

        message = [
            {
                "role": "system",
                "content": policy_prompt,
            },
            {
                "role": "system",
                "content": info_prompt,
            },
            {
                "role": "system",
                "content": task_prompt,
            },
            {
                "role": "assistant",
                "content": role.first_message,
            },
            {
                "role": "user",
                "content": content,
            },
        ]
        print(message)
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
        client = async_chat_factory("siliconflow")(
            "Qwen/Qwen3-Next-80B-A3B-Instruct", -1, OPENAI_BASE_URL, OPENAI_API_KEY
        )
        yield "event: dialog_created\n\n"
        ans: ChatOutput = None
        async for chunk in client.generate(message):
            if ans is None:
                ans = chunk
            else:
                ans += chunk
            yield f"event: output\ndata: {chunk.model_dump_json(exclude_none=True)}\n\n"
        yield f"event: done\n\n"


@role_router.post("/{role_id}/chat")
async def role_chat(
    role_id: PathRoleId,
    user_id: dependencies.DependValidUserId,
    content: Annotated[str, Body(description="对话内容")],
):
    return StreamingResponse(
        create_chat(role_id, content, user_id), media_type="text/event-stream"
    )


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


@role_router.post("/", response_model=schemas.CharacterResponse)
async def role_info(
    form: Annotated[schemas.CharacterCreateForm, Form()],
    user_id: dependencies.DependValidUserId,
    db: dependencies.DependSession,
):
    crud = CharacterCrud(db)
    data = await crud.create_data(form, user_id)
    return data


@world_router.get(
    "/", response_model=PageResponse[schemas.WorldResponse], summary="世界列表"
)
async def world_list(
    query_params: dependencies.DependPageQuery, db: dependencies.DependSession
):
    crud = WorldCrud(db)
    data = await crud.get_datas(query_params.page, query_params.limit)
    total = await crud.get_count()
    return dict(data=data, total=total)


@world_router.get(
    "/{world_id}", response_model=schemas.WorldResponse, summary="世界信息"
)
async def world_info(world_id: PathWorldId, db: dependencies.DependSession):
    crud = WorldCrud(db)
    data = await crud.get_data(world_id, strict=True, scalar=False)
    return data


@world_router.post("/", response_model=schemas.WorldResponse, summary="创建世界")
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
