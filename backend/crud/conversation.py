from operator import attrgetter
from typing import Sequence
from uuid import uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from ..exceptions.common import CustomException, ErrorCode
from ..models import conversation as models
from ..schemas import conversation as schemas
from .base import CrudBase
from .character import CharacterCrud


class SessionCrud(CrudBase[models.ConversationSession, schemas.SessionResponse]):
    _DBModelType = models.ConversationSession
    _DBSchemaType = schemas.SessionResponse

    async def create_data(self, data: schemas.SessionCreateForm, user_id: int):
        title = data.content[:32]
        character_crud = CharacterCrud(self.db)
        characters = await character_crud.get_datas(data_ids=data.character_ids)

        model = self.model(
            **data.model_dump(exclude={"character_ids", "content"}),
            user_id=user_id,
            title=title,
        )
        model.characters.extend(characters)
        model.messages.append(
            models.ConversationHistory(
                session_id=model.id,
                message_id=str(uuid4()),
                role="user",
                content=data.content,
            )
        )
        model = await super().create_data(
            model,
            attribute_names=[
                "created_at",
                "updated_at",
                "user",
                "world",
                "act_character",
                "characters",
                "messages",
            ],
        )
        return model


class ConversationHistoryCrud(
    CrudBase[models.ConversationHistory, schemas.ConversationHistoryResponse]
):
    _DBModelType = models.ConversationHistory
    _DBSchemaType = schemas.ConversationHistoryResponse
