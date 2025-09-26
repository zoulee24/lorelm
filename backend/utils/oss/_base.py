from abc import ABC, abstractmethod
from typing import BinaryIO, Generic, Iterable, List, Optional, TypeVar, Union

from aiohttp import ClientResponse
from miniopy_async import Minio as _Minio

from ..common import BaseTool, DBType


class ObjectStoreServiceBase(BaseTool[DBType], Generic[DBType]):

    @abstractmethod
    async def bucket_exists(self, bucket_name: str) -> bool:
        pass

    @abstractmethod
    async def bucket_create(self, bucket_name: str):
        pass

    @abstractmethod
    async def bucket_delete(self, bucket_name: str):
        pass

    @abstractmethod
    async def bucket_list(self) -> List[str]:
        pass

    @abstractmethod
    async def document_exists(self, bucket_name: str, obj_path: str) -> bool:
        pass

    @abstractmethod
    async def document_get_reader(
        self,
        bucket_name: str,
        obj_path: str,
    ) -> ClientResponse:
        """获取文件流

        :param bucket_name: 存储桶名称
        :type bucket_name: str
        :param obj_path: 文件路径
        :type obj_path: str
        :return: 文件内容（字节）
        :rtype: bytes
        """
        pass

    @abstractmethod
    async def document_get(
        self,
        bucket_name: str,
        obj_path: str,
    ) -> bytes:
        """获取文件

        :param bucket_name: 存储桶名称
        :type bucket_name: str
        :param obj_path: 文件路径
        :type obj_path: str
        :return: 文件内容（字节）
        :rtype: bytes
        """
        pass

    @abstractmethod
    async def document_create(
        self,
        bucket_name: str,
        obj_path: str,
        content: Union[str, bytes, BinaryIO],
        content_size: int = -1,
    ) -> bool:
        """上传文档

        :param bucket_name: 存储桶名称
        :type bucket_name: str
        :param obj_path: 文件路径
        :type obj_path: str
        :param content: 文件内容（字节、字节流）
        :type content: Union[bytes, BinaryIO]
        :param content_size: 文件大小（字节大小）
        :type content_size: int
        :return: 创建状态
        :rtype: bool
        """
        pass

    @abstractmethod
    async def document_list(
        self, bucket_name: str, prefix: Optional[str] = None
    ) -> List[str]:
        pass

    @abstractmethod
    async def document_delete(self, bucket_name: str, obj_path: str) -> List[str]:
        pass

    @abstractmethod
    async def document_mult_delete(
        self, bucket_name: str, objs_path: Iterable[str]
    ) -> None:
        pass
