from abc import abstractmethod
from logging import getLogger
from typing import Final, Generic, List, Optional, Tuple, Union

from typing_extensions import TypeVar

from ...schemas.components import DocumentDict
from ...schemas.profile import SystemProfile
from ..common import BaseTool, DBType

InputType = TypeVar("InputType", bound=Union[str, int, float])

LenAbleVar = Union[List[InputType], Tuple[InputType]]

DEFAULT_QUERY_FIELDS: Final[tuple[str, ...]] = (
    "content_ltks^2",
    "content_sm_ltks",
)


class VectorDatabase(BaseTool[DBType], Generic[DBType]):
    @abstractmethod
    async def index_create(self, index_name: str, vector_dims: int) -> bool:
        """索引创建

        :param index_name: 索引名字
        :type index_name: str
        :param vector_dims: 向量维度
        :type vector_dims: int
        :return: 状态
        :rtype: bool
        """
        pass

    @abstractmethod
    async def index_delete(self, index_name: str) -> bool:
        """索引删除

        :param index_name: 索引名字
        :type index_name: str
        :return: 状态
        :rtype: bool
        """
        pass

    @abstractmethod
    async def index_exists(self, index_name: str) -> bool:
        """索引是否存在

        :param index_name: 索引名字
        :type index_name: str
        :return: 状态
        :rtype: bool
        """
        pass

    @abstractmethod
    async def index_list(self) -> List[str]:
        """索引列表
        :return: 索引列表
        :rtype: List[str]
        """
        pass

    @abstractmethod
    async def doc_delete(
        self,
        index_name: str,
        kbs_id: Optional[Union[int, LenAbleVar[int]]] = None,
        docs_id: Optional[Union[int, LenAbleVar[int]]] = None,
    ):
        pass

    @abstractmethod
    async def doc_count(
        self,
        index_name: str,
        doc_id: Optional[Union[int, LenAbleVar[int]]],
        **kwargs,
    ) -> int:
        """文档块数

        :param index_name: 索引名称
        :type index_name: str
        :param doc_id: 文档ID
        :type doc_id: int | list[int] | None
        :return: 数量
        :rtype: int
        """
        pass

    @abstractmethod
    async def doc_get(
        self,
        index_name: str,
        doc_id: Optional[Union[int, LenAbleVar[int]]],
        includes: Optional[list[str]] = None,
        excludes: Optional[list[str]] = None,
        page: int = 1,
        limit: int = 0,
        **kwargs,
    ) -> list:
        """文档获取

        :param index_name: 索引名称
        :type index_name: str
        :param doc_id: 文档ID
        :type doc_id: int | list[int] | None
        :return: 文档
        :rtype: Document
        """
        pass

    @abstractmethod
    async def doc_insert(self, index_name: str, doc: DocumentDict) -> str:
        """文档插入

        :param index_name: 索引名称
        :type index_name: str
        :param doc: 文档
        :type doc: DocumentDict
        :return: 文档ID
        :rtype: str
        """
        pass

    @abstractmethod
    async def doc_batch_insert(
        self, index_name: str, docs: List[DocumentDict]
    ) -> List[str]:
        """批量文档插入

        :param index_name: 索引名称
        :type index_name: str
        :param docs: 文档列表
        :type docs: List[DocumentDict]
        """
        pass

    @abstractmethod
    async def doc_list(
        self, index_name: str, kb_id: Optional[int] = None, doc_id: Optional[int] = None
    ) -> List[str]:
        """获取文档列表

        :param index_name: 索引名称
        :type index_name: str
        :param kb_id: 知识库id, defaults to None
        :type kb_id: Optional[int], optional
        :param doc_id: 文档id, defaults to None
        :type doc_id: Optional[int], optional
        :return: 文档分块的id列表
        :rtype: List[str]
        """
        pass

    @abstractmethod
    async def search(
        self,
        index_name: Union[str, LenAbleVar[str]],
        kbs_id: Optional[Union[int, LenAbleVar[int]]] = None,
        docs_id: Optional[Union[int, LenAbleVar[int]]] = None,
        query_string: Optional[str] = None,
        query_string_fields: LenAbleVar[str] = DEFAULT_QUERY_FIELDS,
        query_vector: Optional[LenAbleVar[float]] = None,
        top_k: int = 1024,
        vector_similarity: float = 0.1,
        query_vector_weight: float = 0.95,
        includes: Optional[list[str]] = None,
        excludes: Optional[list[str]] = None,
    ) -> List[DocumentDict]:
        """混合检索

        :param index_name: 索引名称
        :type index_name: List[str]
        :param kbs_id: 知识库id, defaults to None
        :type kbs_id: Optional[Union[int, LenAbleVar[int]]], optional
        :param docs_id: 文档id, defaults to None
        :type docs_id: Optional[Union[int, LenAbleVar[int]]], optional
        :param query_string: 查询字符串(强制格式), defaults to None
        :type query_string: Optional[str], optional
        :param query_string_fields: 查询字段, defaults to ( "title_tks^10", "title_sm_tks^5", "important_kwd^30", "important_tks^20", "question_tks^20", "content_ltks^2", "content_sm_ltks", )
        :type query_string_fields: LenAbleVar[str], optional
        :param query_vector: 查询向量, defaults to None
        :type query_vector: Optional[LenAbleVar[float]], optional
        :param top_k: 查询向量top_k, defaults to 1024
        :type top_k: int, optional
        :param vector_similarity: 向量相似度, defaults to 0.1
        :type vector_similarity: float, optional
        :param query_vector_weight: 查询向量权重, defaults to 0.95
        :type query_vector_weight: float, optional
        :return: 文档列表
        :rtype: List[Document]
        """
        pass
