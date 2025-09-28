from operator import attrgetter
from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from ..exceptions.common import CustomException, ErrorCode
from ..models import character as models
from ..schemas import character as schemas
from .base import CrudBase


class LabelCrud(CrudBase[models.Label, schemas.LabelResponse]):
    """
    标签Crud
    """

    _DBModelType = models.Label
    _DBSchemaType = schemas.LabelResponse

    async def batch_create(self, datas: Sequence[str]) -> list[models.Label]:
        models = [self.model(name=it) for it in datas]
        self.db.add_all(models)
        await self.db.flush(models)
        return models

    async def delete_data(self, label_id: int):
        exist = await self.db.scalar(
            select(func.count(models.Lable2Character.id)).where(
                models.Lable2Character.label_id == label_id
            )
        )
        if exist:
            raise CustomException(
                ErrorCode.Exist, "该标签已存在角色中，请先删除角色中的该标签"
            )
        await super().delete_data(label_id)


class WorldCrud(CrudBase[models.World, schemas.WorldResponse]):
    """
    世界Crud
    """

    _DBModelType = models.World
    _DBSchemaType = schemas.WorldResponse

    async def get_data(
        self,
        data_id=None,
        start_sql=None,
        wheres=None,
        select_from=None,
        order=None,
        order_field=None,
        schema=None,
        strict=False,
        scalar=True,
    ):
        return await super().get_data(
            data_id,
            start_sql,
            wheres,
            select_from,
            options=selectinload(self.model.labels),
            order=order,
            order_field=order_field,
            schema=schema,
            strict=strict,
            scalar=scalar,
        )

    async def get_datas(
        self,
        page=1,
        limit=0,
        data_ids=None,
        start_sql=None,
        wheres=None,
        select_from=None,
        order=None,
        order_field=None,
        schema=None,
        scalar=False,
    ):
        return await super().get_datas(
            page,
            limit,
            data_ids,
            start_sql,
            wheres,
            select_from,
            options=selectinload(self.model.labels),
            order=order,
            order_field=order_field,
            schema=schema,
            scalar=scalar,
        )

    async def create_data(self, data: schemas.WorldCreateForm, user_id: int):
        exist = await self.get_count(wheres=self.model.nickname == data.nickname)
        if exist != 0:
            raise CustomException(ErrorCode.Exist)
        label_crud = LabelCrud(self.db)
        exist_label_model = await label_crud.get_datas(
            wheres=label_crud.model.name.in_(data.labels),
            scalar=False,
        )
        not_exist_labels = set(data.labels) - set(
            map(attrgetter("name"), exist_label_model)
        )
        model = self.model(**data.model_dump(exclude={"labels"}), user_id=user_id)
        model.labels.extend(exist_label_model)

        if not_exist_labels:
            not_exist_model = await label_crud.batch_create(not_exist_labels)
            model.labels.extend(not_exist_model)

        return await super().create_data(
            model, attribute_names=["labels", "created_at", "updated_at"]
        )


class CharacterCrud(CrudBase[models.Character, schemas.CharacterResponse]):
    """
    角色Crud
    """

    _DBModelType = models.Character
    _DBSchemaType = schemas.CharacterResponse

    async def get_data(
        self,
        data_id=None,
        start_sql=None,
        wheres=None,
        select_from=None,
        options=None,
        order=None,
        order_field=None,
        schema=None,
        strict=False,
        scalar=True,
    ):
        _options = [selectinload(self.model.labels)]
        if options is not None:
            if isinstance(options, list):
                _options.extend(options)
            else:
                _options.append(options)

        return await super().get_data(
            data_id,
            start_sql,
            wheres,
            select_from,
            options=_options,
            order=order,
            order_field=order_field,
            schema=schema,
            strict=strict,
            scalar=scalar,
        )

    async def get_datas(
        self,
        page=1,
        limit=0,
        data_ids=None,
        start_sql=None,
        wheres=None,
        select_from=None,
        options=None,
        order=None,
        order_field=None,
        schema=None,
        scalar=False,
    ):
        _options = [selectinload(self.model.labels)]
        if options is not None:
            if isinstance(options, list):
                _options.extend(options)
            else:
                _options.append(options)
        return await super().get_datas(
            page,
            limit,
            data_ids,
            start_sql,
            wheres,
            select_from,
            options=_options,
            order=order,
            order_field=order_field,
            schema=schema,
            scalar=scalar,
        )

    async def create_data(self, data: schemas.CharacterCreateForm, user_id: int):
        exist = await self.get_count(wheres=self.model.nickname == data.nickname)
        if exist != 0:
            raise CustomException(ErrorCode.Exist)
        label_crud = LabelCrud(self.db)
        exist_label_model = await label_crud.get_datas(
            wheres=label_crud.model.name.in_(data.labels),
            scalar=False,
        )
        not_exist_labels = set(data.labels) - set(
            map(attrgetter("name"), exist_label_model)
        )
        model = self.model(
            **data.model_dump(exclude={"labels", "relate_world_id", "avatar", "files"}),
            user_id=user_id,
        )
        model.labels.extend(exist_label_model)

        if not_exist_labels:
            not_exist_model = await label_crud.batch_create(not_exist_labels)
            model.labels.extend(not_exist_model)

        return await super().create_data(
            model, attribute_names=["labels", "created_at", "updated_at", "world"]
        )


class DocumentCrud(CrudBase[models.Document, schemas.DocumentResponse]):
    """
    文档Crud
    """

    _DBModelType = models.Document
    _DBSchemaType = schemas.DocumentResponse
