import asyncio
import os
from datetime import datetime, timedelta
from operator import attrgetter, itemgetter
from typing import Annotated, Optional
from uuid import uuid4

import aiohttp
from fastapi import APIRouter, Body, Form, Path, Query
from fastapi.responses import StreamingResponse
from omni_llm import (
    AsyncChatBase,
    ChatOutput,
    async_chat_factory,
    async_embedding_factory,
)
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from backend import dependencies
from backend.crud import SessionCrud
from backend.exceptions import CustomException, ErrorCode
from backend.models import conversation as models
from backend.prompts import get_prompt_template
from backend.schemas import PageResponse
from backend.schemas import conversation as schemas
from backend.utils.nlp import FullTextQueryer
from backend.utils.vector import get_vdb_with

conversation_router = APIRouter(prefix="/conversation", tags=["对话"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")
OPENAI_EMBED_DIMS = int(os.getenv("OPENAI_EMBED_DIMS"))
QINIU_API_KEY = os.getenv("QINIU_API_KEY")
assert OPENAI_EMBED_DIMS == 1024, "OPENAI_EMBED_DIMS must be 1024"


@conversation_router.get(
    "", response_model=list[schemas.SessionResponse], summary="30天内会话列表"
)
async def conversation_session_list(
    db: dependencies.DependSession, user_id: dependencies.DependValidUserId
):
    crud = SessionCrud(db)
    now = datetime.now()
    return await crud.get_datas(
        wheres=and_(
            crud.model.user_id == user_id,
            (now - crud.model.updated_at) < timedelta(days=30),
        ),
        order="desc",
        order_field="updated_at",
    )


@conversation_router.get(
    "/{session_id}", response_model=schemas.SessionMessageResponse, summary="获取会话"
)
async def conversation_session_info(
    db: dependencies.DependSession,
    session_id: Annotated[int, Path(description="会话ID")],
):
    crud = SessionCrud(db)
    return await crud.get_data(
        session_id,
        options=[
            joinedload(crud.model.world),
            joinedload(crud.model.act_character).joinedload(models.Character.labels),
            selectinload(crud.model.characters).joinedload(models.Character.labels),
            selectinload(crud.model.messages),
        ],
    )


@conversation_router.post(
    "", response_model=schemas.SessionMessageResponse, summary="创建会话"
)
async def conversation_session_create(
    user_id: dependencies.DependValidUserId,
    db: dependencies.DependSession,
    form: schemas.SessionCreateForm = Body(description="会话创建表单"),
):
    crud = SessionCrud(db)
    session = await crud.create_session(form, user_id)
    return session


@conversation_router.post("/{session_id}", summary="继续会话")
async def conversation_session_chat(
    user_id: dependencies.DependValidUserId,
    session_id: int = Path(description="会话ID"),
    content: str = Body(embed=True, description="会话创建表单"),
):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    if not all([OPENAI_API_KEY, OPENAI_BASE_URL]):
        raise CustomException(ErrorCode.Other, "系统错误")
    client = async_chat_factory("siliconflow")(
        "Qwen/Qwen3-Next-80B-A3B-Instruct", -1, OPENAI_BASE_URL, OPENAI_API_KEY
    )
    return StreamingResponse(
        create_chat(content, user_id, session_id, client),
        media_type="text/event-stream",
    )


async def create_chat(
    query: str,
    user_id: int,
    session_id: int,
    client: AsyncChatBase,
):
    quweyer = FullTextQueryer()
    embed_md = async_embedding_factory("siliconflow")(
        OPENAI_EMBED_MODEL,
        -1,
        OPENAI_EMBED_DIMS,
        OPENAI_BASE_URL,
        OPENAI_API_KEY,
    )
    (query_string, _), embed_result = await asyncio.gather(
        asyncio.to_thread(quweyer.question, query), embed_md.encode([query])
    )
    query_vector: list[float] = embed_result.v[0].tolist()
    async with dependencies.get_session_with() as db, get_vdb_with() as vdb:
        crud = SessionCrud(db)

        session = await crud.get_data(
            session_id,
            wheres=crud.model.user_id == user_id,
            options=[
                selectinload(crud.model.messages),
                selectinload(crud.model.characters),
                joinedload(crud.model.act_character),
                joinedload(crud.model.world),
                joinedload(crud.model.user),
            ],
            strict=True,
            scalar=True,
        )
        if not session.title or len(session.messages) < 2:
            session.title = query[:32]
        session.messages.append(
            models.ConversationHistory(
                session_id=session.id,
                message_id=str(uuid4()),
                role="user",
                content=query,
            )
        )
        session = await crud.update_data(
            session, attribute_names=["updated_at", "messages"]
        )

        roles_name = (
            "[" + ", ".join(map(lambda x: f'"{x.nickname}"', session.characters)) + "]"
        )

        task_prompt = get_prompt_template("task").render(
            roles_name=roles_name, user=session.user, language=session.user.language
        )
        policy_prompt = get_prompt_template("policy").render(
            roles_name=roles_name,
            user=session.user,
            jailbreak=True,
            policy=True,
            language=session.user.language,
        )
        info_prompt = get_prompt_template("info").render(
            roles=session.characters, user=session.user, language=session.user.language
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
        ]
        message.extend(
            dict(role=message.role, content=message.content)
            for message in session.messages
        )

        yield "event: dialog_created\ndata: {}\n\n".format(
            schemas.ConversationHistoryResponse.model_validate(
                session.messages[-1]
            ).model_dump_json()
        )

        yield 'event: notice\ndata: {"content": "搜索世界知识中"}\n\n'
        search_result = await vdb.search(
            "lorelm",
            worlds_id=session.world.id if session.world else None,
            roles_id=list(map(attrgetter("id"), session.characters)),
            query_string=query_string,
            query_vector=query_vector,
            includes=["content"],
        )
        if search_result:
            print(f"检索到 {len(search_result)} 条知识")
            kb_prompt = get_prompt_template("lorebook").render(
                knowledgebase=map(itemgetter("content"), search_result)
            )
            message.append(
                {
                    "role": "system",
                    "content": kb_prompt,
                }
            )

        ans: ChatOutput = None
        async for chunk in client.generate(message):
            if ans is None:
                ans = chunk
                session.messages.append(
                    models.ConversationHistory(
                        session_id=session.id,
                        message_id=ans.id,
                        role="assistant",
                        content="",
                        reasoning="",
                        token_usage=0,
                    )
                )
                session = await crud.update_data(
                    session, attribute_names=["messages", "updated_at"]
                )
                yield "event: dialog_created\ndata: {}\n\n".format(
                    schemas.ConversationHistoryResponse.model_validate(
                        session.messages[-1]
                    ).model_dump_json()
                )
            else:
                ans += chunk
            yield f"event: output\ndata: {chunk.model_dump_json(exclude_none=True)}\n\n"

        async with aiohttp.ClientSession() as se:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {QINIU_API_KEY}",
            }
            data = {
                "audio": {
                    "voice_type": "qiniu_zh_female_tmjxxy",
                    "encoding": "mp3",
                    "speed_ratio": 1.0,
                },
                "request": {"text": ans.content},
            }
            async with se.post(
                "https://openai.qiniu.com/v1/voice/tts", headers=headers, json=data
            ) as response:
                if response.status == 200:
                    data = await response.content.read()
                    yield b"event: tts\ndata: " + data + b"\n\n"
                else:
                    data = await response.content.read()
                    print(response.status)

        # 结束对话
        yield f"event: done\n\n"
        # 更新token使用量
        session.messages[-1].content = ans.content
        session.messages[-1].reasoning = ans.reasoning
        session.messages[-1].token_usage = ans.usage.prompt_tokens
        session.token_usage += ans.usage.total_tokens
        session = await crud.update_data(session)
