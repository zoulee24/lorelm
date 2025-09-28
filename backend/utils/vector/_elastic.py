from copy import deepcopy
from typing import Optional, Set, Tuple, Union

import yaml
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.response import Hit
from elasticsearch.dsl.utils import recursive_to_dict

from ...schemas.components import DocumentDict
from ...schemas.profile import ProfileProvider
from ...utils import get_root_dir
from ._base import DEFAULT_QUERY_FIELDS, LenAbleVar, VectorDatabase

# num_candidates 最大值为10,000
# https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query
MAX_CANDIDATES = 10000


class ElasticSearch(VectorDatabase[AsyncElasticsearch]):
    """ElasticSearch vector database"""

    # 元数据
    type = ProfileProvider.ElasticSearch

    def __init__(self, *args, **kwargs):
        super(ElasticSearch, self).__init__(*args, **kwargs)
        with open(
            get_root_dir("resources/vector/es/config.yml"), encoding="utf-8"
        ) as f:
            self._setting = yaml.load(f, Loader=yaml.FullLoader)
        assert (
            "mapping" in self._setting and "setting" in self._setting
        ), "elasticsearch config error"

    def _get_client(self):
        return AsyncElasticsearch(
            "http://{host}:{port}".format(
                host=self._config.host, port=self._config.port
            ),
            basic_auth=(self._config.username, self._config.password),
        )

    async def index_create(self, index_name: str, vector_dims: int) -> bool:
        if await self.index_exists(index_name):
            self.logger.warning(f"op create, index {index_name} already exists")
            return False
        mapping = deepcopy(self._setting["mapping"])
        mapping["properties"]["vector"]["dims"] = vector_dims
        await self._client.indices.create(
            index=index_name,
            mappings=mapping,
            settings=self._setting["setting"],
        )
        self.logger.info(f"op create, index {index_name} created")
        return True

    async def index_delete(self, index_name: str) -> bool:
        if not await self.index_exists(index_name):
            self.logger.warning(f"op delete, index {index_name} not exists")
            return False
        await self._client.indices.delete(index=index_name)
        self.logger.info(f"op delete, index {index_name} deleted")
        return True

    async def index_exists(self, index_name: str) -> bool:
        return await self._client.indices.exists(index=index_name)

    async def index_list(self) -> list[str]:
        indices = await self._client.cat.indices(format="json")
        return [index["index"] for index in indices]

    async def doc_list(
        self, index_name: str, kb_id: Optional[int] = None, doc_id: Optional[int] = None
    ) -> list[str]:
        s = AsyncSearch(using=self._client, index=index_name).source(includes=["_id"])
        if kb_id is not None:
            s = s.filter("term", kb_id=kb_id)
        if doc_id is not None:
            s = s.filter("term", doc_id=doc_id)
        rsp = await s.execute()
        return [hit.meta.id for hit in rsp.hits]

    async def doc_delete(
        self,
        index_name: str,
        kbs_id: Optional[Union[int, LenAbleVar[int]]] = None,
        docs_id: Optional[Union[int, LenAbleVar[int]]] = None,
    ):
        s = AsyncSearch(using=self._client, index=index_name)
        if kbs_id is not None:
            s = s.filter("term" if isinstance(kbs_id, int) else "terms", kb_id=kbs_id)
        if docs_id is not None:
            s = s.filter(
                "term" if isinstance(docs_id, int) else "terms", doc_id=docs_id
            )
        rsp = await self._client.delete_by_query(index=index_name, body=s.to_dict())

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
        s = AsyncSearch(using=self._client, index=index_name)
        if doc_id is not None:
            s = s.filter(
                "terms" if isinstance(doc_id, (list, Tuple, Set)) else "term",
                doc_id=doc_id,
            )
        for k, v in kwargs.items():
            s = s.filter(
                "terms" if isinstance(v, (list, Tuple, Set)) else "term", **{k: v}
            )
        return await s.count()

    async def doc_get(
        self,
        index_name: str,
        doc_id: Optional[Union[int, LenAbleVar[int]]] = None,
        includes: Optional[list[str]] = None,
        excludes: Optional[list[str]] = None,
        page: int = 1,
        limit: int = 0,
        **kwargs,
    ) -> list[Hit]:
        s = AsyncSearch(using=self._client, index=index_name)
        if includes is not None:
            s = s.source(includes=includes)
        if excludes is not None:
            s = s.source(excludes=excludes)
        if limit > 0 and page > 0:
            s = s.extra(from_=limit * (page - 1), size=limit)
        if doc_id is not None:
            s = s.filter(
                "terms" if isinstance(doc_id, (list, Tuple, Set)) else "term",
                doc_id=doc_id,
            )
        for k, v in kwargs.items():
            s = s.filter(
                "terms" if isinstance(v, (list, Tuple, Set)) else "term", **{k: v}
            )
        # # 排序
        # s = s.sort("-create_at")
        rsp = await s.execute()
        for hit in rsp.hits:
            hit["id"] = hit.meta.id
        return recursive_to_dict(rsp.hits)

    async def doc_insert(self, index_name: str, doc: DocumentDict) -> str:
        rsp = await self._client.index(index=index_name, document=doc)
        return rsp["index"]["_id"]

    async def doc_batch_insert(
        self, index_name: str, docs: list[DocumentDict]
    ) -> list[str]:
        batch_size = 32
        operations = list()
        outputs = list()
        for doc in docs:
            operations.append({"index": {"_index": index_name}})
            operations.append(doc)
        for i in range(0, len(operations), batch_size):
            rsp = await self._client.bulk(operations=operations[i : i + batch_size])
            if rsp["errors"]:
                raise Exception(rsp["errors"])
            outputs.extend(it["index"]["_id"] for it in rsp["items"])
        self.logger.info(f"index:{index_name} create {len(outputs)} docs success")
        return outputs

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
    ) -> list[DocumentDict]:
        s = AsyncSearch(
            using=self._client, index=index_name, extra=dict(timeout="600s")
        )
        if includes is not None:
            s = s.source(includes=includes)
        if excludes is not None:
            s = s.source(excludes=excludes)

        # # 过滤
        # s = s.filter("term", disabled=False)
        if kbs_id:
            s = (
                s.filter("term", kb_id=kbs_id)
                if isinstance(kbs_id, int)
                else s.filter("terms", kb_id=kbs_id)
            )
        if docs_id:
            # 查询 元数据里面的 id 字段
            s = (
                s.filter("term", doc_id=docs_id)
                if isinstance(docs_id, int)
                else s.filter("terms", doc_id=docs_id)
            )
        if query_string:
            s = s.query(
                "query_string",
                query=query_string,
                minimum_should_match="30%",
                fields=list(query_string_fields),
                type="best_fields",
                boost=1,
            )
        if query_vector is not None:
            s.query.boost = 1 - query_vector_weight
            s = s.knn(
                "vector",
                top_k,
                min(top_k * 2, MAX_CANDIDATES),
                query_vector,
                filter=s.query.to_dict(),
                similarity=vector_similarity,
            )

        # import json

        # with open("query.json", "w") as f:
        #     json.dump(s.to_dict(), f, ensure_ascii=False, indent=2)

        rsp = await s.execute()
        # TODO 优化这个id的提取
        for hit in rsp.hits:
            hit["id"] = hit.meta.id
        # return TypeAdapter(list[Document]).validate_python(rsp.hits)
        return recursive_to_dict(rsp.hits)

    async def close(self):
        await self._client.close()
