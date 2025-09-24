import os
from datetime import datetime, timedelta
from operator import attrgetter
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, Body, Form, Path, Query
from fastapi.responses import StreamingResponse
from omni_llm import AsyncChatBase, ChatOutput, async_chat_factory
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

conversation_router = APIRouter(prefix="/conversation", tags=["对话"])


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
        )
    )


@conversation_router.post("", summary="创建会话")
async def conversation_session_list(
    form: schemas.SessionCreateForm,
    user_id: dependencies.DependValidUserId,
    session_id: Optional[int] = Query(None, description="会话ID"),
):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    if not all([OPENAI_API_KEY, OPENAI_BASE_URL]):
        raise CustomException(ErrorCode.Other, "系统错误")
    client = async_chat_factory("siliconflow")(
        "Qwen/Qwen3-Next-80B-A3B-Instruct", -1, OPENAI_BASE_URL, OPENAI_API_KEY
    )
    return StreamingResponse(
        create_chat(form, user_id, session_id, client),
        media_type="text/event-stream",
    )


async def create_chat(
    form: schemas.SessionCreateForm,
    user_id: int,
    session_id: int,
    client: AsyncChatBase,
):
    async with dependencies.get_session_with() as db:
        crud = SessionCrud(db)
        if session_id is not None:
            session = await crud.get_data(
                session_id,
                options=[
                    selectinload(crud.model.characters),
                    joinedload(crud.model.act_character),
                    joinedload(crud.model.world),
                    joinedload(crud.model.user),
                ],
                strict=True,
                scalar=True,
            )
            session.messages.append(
                models.ConversationHistory(
                    session_id=session.id,
                    message_id=str(uuid4()),
                    role="user",
                    content=form.content,
                )
            )
            session = await crud.update_data(
                session, attribute_names=["updated_at", "messages"]
            )
        else:
            session = await crud.create_data(form, user_id)
            yield "event: session_created\ndata: {}\n\n".format(
                schemas.SessionFullResponse.model_validate(session).model_dump_json()
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
            {
                "role": "assistant",
                "content": session.characters[0].first_message,
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
        ans: ChatOutput = None
        async for chunk in client.generate(message):
            if ans is None:
                ans = chunk
            else:
                ans += chunk
            yield f"event: output\ndata: {chunk.model_dump_json(exclude_none=True)}\n\n"
        # 结束对话
        yield f"event: done\n\n"
        # 更新token使用量
        session.messages[-1].token_usage = ans.usage.prompt_tokens
        session.messages.append(
            models.ConversationHistory(
                session_id=session.id,
                message_id=ans.id,
                role="assistant",
                content=ans.content,
                reasoning=ans.reasoning,
                token_usage=ans.usage.completion_tokens,
            )
        )
        session.token_usage += ans.usage.total_tokens
        session = await crud.update_data(session)
        yield f"event: done\n\n"
