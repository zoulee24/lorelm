import asyncio
from operator import attrgetter
from typing import List, Type

from pydantic import BaseModel, TypeAdapter
from sqlalchemy import Delete, Update, asc, desc, false, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.selectable import ColumnElement, FromClause, Select
from typing_extensions import (
    Any,
    Dict,
    Generic,
    Iterable,
    Literal,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from backend.exceptions import CustomException, ErrorCode

from ..models import DbBase

DB_MODEL_TYPE = TypeVar("DB_MODEL_TYPE", bound=DbBase)
DB_SCHEMA_TYPE = TypeVar("DB_SCHEMA_TYPE", bound=BaseModel)
DBIdType = TypeVar("DBIdType", default=int, infer_variance=True)

INPUT_SCHEMA_TYPE = TypeVar("INPUT_SCHEMA_TYPE", bound=BaseModel, infer_variance=True)
OUTPUT_SCHEMA_TYPE = TypeVar("OUTPUT_SCHEMA_TYPE", bound=BaseModel, infer_variance=True)

type CSOption[T] = Union[List[T], Tuple[T, ...], None]
type CSSOption[T] = Union[CSOption[T], T, None]


class CrudBase(Generic[DB_MODEL_TYPE, DB_SCHEMA_TYPE]):
    __type_params__ = (DB_MODEL_TYPE, DB_SCHEMA_TYPE)
    # class CrudBase:
    __ORDER_FIELD = ("desc", "descending")
    _DBModelType: Type[DB_MODEL_TYPE] = DbBase
    _DBSchemaType: Type[DB_SCHEMA_TYPE] = BaseModel

    def __init__(
        self,
        db: AsyncSession,
    ):
        self._db = db
        self._lock = asyncio.Lock()

    @property
    def db(self) -> AsyncSession:
        return self._db

    @property
    def model(self) -> Type[DB_MODEL_TYPE]:
        return self._DBModelType

    @property
    def schema(self) -> Type[DB_SCHEMA_TYPE]:
        return self._DBSchemaType

    async def get_id(
        self,
        data_id: DBIdType,
        field: str = "id",
        wheres: CSSOption[ColumnElement[bool]] = None,
        *,
        strict=False,
    ):
        id_column = getattr(self.model, field)
        sql = Select(id_column).where(id_column == data_id).limit(1)
        sql = self._filter(sql, wheres)
        _id = (await self.execute(sql)).scalar_one_or_none()
        if strict and _id is None:
            raise CustomException(ErrorCode.NotExist)
        if _id is not None:
            return cast(DBIdType, _id)
        return None

    async def execute(
        self,
        start_sql: Select,
        wheres: CSSOption[ColumnElement[bool]] = None,
        select_from: CSSOption[FromClause] = None,
        options: CSSOption[ExecutableOption] = None,
        order: Optional[Literal["desc", "descending"]] = None,
        order_field: Optional[str] = None,
    ):
        sql = self._filter(start_sql, wheres, select_from, options, order, order_field)
        async with self._lock:
            return await self._db.execute(sql)

    async def get_count(
        self,
        start_sql: Optional[Select] = None,
        wheres: CSOption[ColumnElement[bool]] = None,
        select_from: CSSOption[FromClause] = None,
        options: CSOption[ExecutableOption] = None,
        order: Optional[Literal["desc", "descending"]] = None,
        order_field: Optional[str] = None,
    ) -> int:
        sql = start_sql or Select(func.count(self._DBModelType.id))
        return (
            await self.execute(sql, wheres, select_from, options, order, order_field)
        ).scalar_one()

    async def get_data(
        self,
        data_id: Optional[DBIdType] = None,
        start_sql: Optional[Select] = None,
        wheres: CSSOption[ColumnElement[bool]] = None,
        select_from: CSSOption[FromClause] = None,
        options: CSSOption[ExecutableOption] = None,
        order: Optional[Literal["desc", "descending"]] = None,
        order_field: Optional[str] = None,
        schema: Optional[Union[OUTPUT_SCHEMA_TYPE, bool]] = None,
        strict: bool = False,
        scalar: bool = True,
    ):
        is_start_sql_none = start_sql is None
        start_sql = Select(self._DBModelType) if is_start_sql_none else start_sql
        start_sql = start_sql.limit(1)
        if data_id is not None:
            start_sql = start_sql.where(self._DBModelType.id == data_id)

        sql = self._filter(start_sql, wheres, select_from, options, order, order_field)
        async with self._lock:
            result = await self._db.execute(sql)
        if options is not None:
            result = result.unique()
        if scalar:
            model = result.scalar_one_or_none()
        else:
            model = result.one_or_none()

        # model = cast(Optional[DB_MODEL_TYPE], result)

        if model is None:
            if strict:
                raise CustomException(ErrorCode.NotExist)
            return None

        if schema is not None:
            if isinstance(schema, bool):
                if schema:
                    return self.schema.model_validate(model)
            else:
                return schema.model_validate(model)
        if not scalar and is_start_sql_none:
            model = getattr(model, self._DBModelType.__name__)
        return model

    async def get_datas(
        self,
        page: int = 1,
        limit: int = 0,
        data_ids: CSOption[DBIdType] = None,
        start_sql: Optional[Select] = None,
        wheres: CSSOption[ColumnElement[bool]] = None,
        select_from: CSSOption[FromClause] = None,
        options: CSSOption[ExecutableOption] = None,
        order: Optional[Literal["desc", "descending"]] = None,
        order_field: Optional[str] = None,
        schema: Optional[OUTPUT_SCHEMA_TYPE] = None,
        scalar: bool = False,
    ):
        is_start_sql_none = start_sql is None
        if is_start_sql_none:
            start_sql = Select(self._DBModelType)
        if data_ids is not None:
            start_sql = start_sql.where(self._DBModelType.id.in_(data_ids))

        sql = self._filter(start_sql, wheres, select_from, options, order, order_field)

        if limit > 0:
            sql = sql.offset((page - 1) * limit).limit(limit)
        # # 打印sql
        # print(str(sql.compile(compile_kwargs={"literal_binds": True})))

        func = self._db.scalars if scalar else self._db.execute

        async with self._lock:
            results = await func(sql)

        models = cast(
            List[DB_MODEL_TYPE],
            results.all() if options is None else results.unique().all(),
        )
        if schema is not None:
            if isinstance(schema, bool):
                if schema:
                    return TypeAdapter(List[self.schema]).validate_python(models)
            else:
                return TypeAdapter(List[schema]).validate_python(models)
        if not scalar and is_start_sql_none:
            models = list(map(attrgetter(self._DBModelType.__name__), models))
        return models

    async def create_data(
        self,
        data: Union[DB_MODEL_TYPE, INPUT_SCHEMA_TYPE, Dict[str, Any]],
        schema: Optional[OUTPUT_SCHEMA_TYPE] = None,
        auto_flush: bool = True,
        attribute_names: Optional[Iterable[str]] = None,
    ):
        if isinstance(data, Dict):
            model = cast(DB_MODEL_TYPE, self._DBModelType(**data))
        elif isinstance(data, BaseModel):
            model = cast(DB_MODEL_TYPE, self._DBModelType(**data.model_dump()))
        elif isinstance(data, self._DBModelType):
            model = cast(DB_MODEL_TYPE, data)
        else:
            raise ValueError(f"Invalid data type: {type(data)}")
        self._db.add(model)
        if auto_flush:
            await self.flush(model, attribute_names)

        if schema is not None:
            if isinstance(schema, bool):
                if schema:
                    return self.schema.model_validate(model)
            else:
                return schema.model_validate(model)
        return model

    async def update_data(
        self,
        data: Union[DB_MODEL_TYPE, INPUT_SCHEMA_TYPE, Dict[str, Any]],
        data_id: Optional[DBIdType] = None,
        schema: Optional[OUTPUT_SCHEMA_TYPE] = None,
        auto_flush: bool = True,
        attribute_names: Optional[Iterable[str]] = None,
    ):
        if data_id is None and not isinstance(data, self._DBModelType):
            raise ValueError("data_id is required when data is not a model")
        if isinstance(data, (Dict, BaseModel)):
            model = await self.get_data(data_id)
            if model is None:
                raise CustomException(ErrorCode.NotExist)
            if isinstance(data, BaseModel):  # pragma: no cover
                data = data.model_dump(mode="json")
            for k, v in data.items():
                setattr(model, k, v)
        elif isinstance(data, self._DBModelType):
            model = cast(DB_MODEL_TYPE, data)
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

        if auto_flush:
            await self.flush(model, attribute_names)

        if schema is not None:
            if isinstance(schema, bool):
                if schema:
                    return self.schema.model_validate(model)
            else:
                return schema.model_validate(model)
        return model

    async def delete_data(
        self,
        data_id: Optional[DBIdType] = None,
        wheres: CSSOption[ColumnElement[bool]] = None,
        strict: bool = False,
        soft: bool = True,
    ):
        if strict:
            await self.get_id(data_id, strict=True)
        sql = (
            Update(self._DBModelType).values(
                is_delete=True, deleted_at=func.current_timestamp()
            )
            if soft
            else Delete(self._DBModelType)
        )
        if data_id is not None:
            sql = sql.where(self._DBModelType.id == data_id)
        if wheres is not None:
            sql = self._filter(sql, wheres)
        await self._db.execute(sql)
        await self.flush()

    async def delete_datas(self, data_ids: Iterable[DBIdType], soft: bool = True):
        sql = (
            Update(self._DBModelType).values(
                is_delete=True, deleted_at=func.current_timestamp()
            )
            if soft
            else Delete(self._DBModelType)
        ).where(self._DBModelType.id.in_(data_ids))
        await self._db.execute(sql)
        await self.flush()

    async def flush(
        self,
        obj: Optional[DB_MODEL_TYPE] = None,
        attribute_names: Optional[Iterable[str]] = None,
    ):
        async with self._lock:
            await self._db.flush()
            if obj is not None:
                await self._db.refresh(obj, attribute_names=attribute_names)

    def _filter(
        self,
        start_sql: Select,
        wheres: CSSOption[ColumnElement[bool]] = None,
        select_from: CSSOption[FromClause] = None,
        options: CSSOption[ExecutableOption] = None,
        order: Optional[Literal["desc", "descending"]] = None,
        order_field: Optional[str] = None,
    ):
        sql = start_sql.where(self._DBModelType.is_delete == false())

        if select_from is not None:
            if isinstance(select_from, (List, Tuple)):
                sql = sql.select_from(*select_from)
            else:
                sql = sql.select_from(select_from)

        if wheres is not None:
            if isinstance(wheres, (List, Tuple)):
                sql = sql.where(*wheres)
            else:
                sql = sql.where(wheres)
        if options is not None:
            if isinstance(options, (List, Tuple)):
                sql = sql.options(*options)
            else:
                sql = sql.options(options)

        if order_field is not None and order in self.__ORDER_FIELD:
            sql = sql.order_by(desc(getattr(self._DBModelType, order_field)))
        elif order_field is not None:
            sql = sql.order_by(asc(getattr(self._DBModelType, order_field)))

        return sql
