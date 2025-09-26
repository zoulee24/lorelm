import json
import mimetypes
from io import BytesIO
from sys import version_info
from typing import BinaryIO, Iterable, List, Optional, Union

from aiohttp import ClientResponse
from miniopy_async import Minio as _Minio
from miniopy_async.deleteobjects import DeleteObject
from miniopy_async.error import S3Error
from miniopy_async.helpers import check_bucket_name, check_object_name

from backend.schemas import ProfileProvider
from backend.utils import get_root_dir

from ._base import ObjectStoreServiceBase


class Minio(ObjectStoreServiceBase[_Minio]):
    type = ProfileProvider.Minio
    with open(get_root_dir("resources/oss/minio/policy.json"), encoding="utf-8") as f:
        __policy = json.dumps(json.load(f))

    def _get_client(self) -> _Minio:
        """获取数据库客户端"""
        return _Minio(
            f"{self._config.host}:{self._config.port}",
            self._config.username,
            self._config.password,
            secure=self._config.extra.get("secure", True),
        )

    async def bucket_exists(self, bucket_name: str) -> bool:
        return await self._client.bucket_exists(bucket_name)

    async def bucket_create(self, bucket_name: str):
        try:
            check_bucket_name(bucket_name)
        except ValueError:
            self.logger.warning(f"存储桶命名不符合规范: {bucket_name}")
            return False
        if await self.bucket_exists(bucket_name):
            self.logger.warning(f"Bucket {bucket_name} already exists")
            return True
        await self._client.make_bucket(bucket_name)
        await self._client.set_bucket_policy(
            bucket_name, self.__policy.replace("bucket_name", bucket_name)
        )
        self.logger.info(f"Bucket {bucket_name} created")
        return True

    async def bucket_delete(self, bucket_name: str):
        if not await self.bucket_exists(bucket_name):
            self.logger.warning(f"Bucket {bucket_name} does not exist")
            return
        await self._client.remove_bucket(bucket_name)
        self.logger.info(f"Bucket {bucket_name} deleted")

    async def bucket_list(self) -> List[str]:
        buckets = await self._client.list_buckets()
        return [bucket.name for bucket in buckets]

    async def document_exists(self, bucket_name: str, obj_path: str) -> bool:
        try:
            check_object_name(obj_path)
        except ValueError:
            self.logger.warning(f"文件路径或文件名错误: {obj_path}")
            return False
        flag = False
        try:
            result = await self._client.get_object_tags(bucket_name, obj_path)
            flag = True
        except S3Error as e:
            if e.code != "NoSuchKey":
                self.logger.warning(f"op doc exists: {e}")
        return flag

    async def document_get_reader(
        self,
        bucket_name: str,
        obj_path: str,
    ) -> ClientResponse:
        rsp = await self._client.get_object(bucket_name, obj_path)
        # print(rsp.status)
        if rsp.status != 200:
            self.logger.error(
                f"桶 {bucket_name} 获取文件 {obj_path} 失败, code: {rsp.status}"
            )
            raise S3Error("get fail", "获取文件失败")
        return rsp

    async def document_get(
        self,
        bucket_name: str,
        obj_path: str,
    ) -> bytes:
        rsp = await self._client.get_object(bucket_name, obj_path)
        # print(rsp.status)
        if rsp.status != 200:
            self.logger.error(
                f"桶 {bucket_name} 获取文件 {obj_path} 失败, code: {rsp.status}"
            )
            raise S3Error("get fail", "获取文件失败")
        content = await rsp.content.read()
        return content

    async def document_create(
        self,
        bucket_name: str,
        obj_path: str,
        content: Union[str, bytes, BinaryIO],
        content_size: int = -1,
    ) -> bool:
        try:
            check_object_name(obj_path)
        except ValueError:
            self.logger.warning(f"文件路径或文件名错误: {obj_path}")
            return False
        if await self.document_exists(bucket_name, obj_path):
            self.logger.warning(f"桶 {bucket_name} 文件已经存在: {obj_path}, 即将覆盖")
            # return False
        func = (
            mimetypes.guess_file_type
            if version_info >= (3, 13)
            else mimetypes.guess_type
        )
        content_type = func(obj_path)[0] or "application/octet-stream"

        if isinstance(content, str):
            content = BytesIO(content.encode("utf-8"))
        elif isinstance(content, bytes):
            content = BytesIO(content)

        flag = False
        try:
            await self._client.put_object(
                bucket_name,
                obj_path,
                content,
                content_size,
                content_type,
                num_parallel_uploads=1,
            )
            self.logger.info(f"bucket {bucket_name} upload {obj_path} file")
            flag = True
        except Exception as e:
            self.logger.error(e)
        return flag

    async def document_list(
        self, bucket_name: str, prefix: Optional[str] = None
    ) -> List[str]:
        results = await self._client.list_objects(bucket_name, prefix, recursive=True)
        return [it.object_name for it in results]

    async def document_delete(self, bucket_name: str, obj_path: str) -> List[str]:
        self.logger.info(f"delete {bucket_name} {obj_path}")
        await self._client.remove_object(bucket_name, obj_path)

    async def document_mult_delete(
        self, bucket_name: str, objs_path: Iterable[str]
    ) -> None:
        for obj_path in objs_path:
            self.logger.info(f"delete {bucket_name} {obj_path}")
        async for error in self._client.remove_objects(
            bucket_name, (DeleteObject(it) for it in objs_path)
        ):
            if error:
                self.logger.error(error)

    async def close(self):
        await self._client.close_session()
