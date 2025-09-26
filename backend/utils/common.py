import hashlib
import os.path
import time
from abc import ABC, abstractmethod
from io import BytesIO
from logging import getLogger
from typing import Final, Generic, Optional, TypeVar

from backend.schemas import ProfileProvider, SystemProfile


def get_unix_timestamp():
    """
    Returns the current Unix timestamp.
    """
    return int(time.time() * 1e3)


def get_root_dir(path: Optional[str] = None) -> str:
    """
    Returns the root directory of the project.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return root_dir if path is None else os.path.join(root_dir, path)


def calculate_file_hash(fp: BytesIO, chunk_size: int = 8192) -> str:
    """计算二进制文件的哈希值"""
    hash_obj = hashlib.sha256()

    # 分块读取文件并计算哈希
    try:
        while chunk := fp.read(chunk_size):
            hash_obj.update(chunk)
    except IOError as e:
        raise IOError(f"文件读取错误: {e}") from e
    fp.seek(0)
    return hash_obj.hexdigest()


def parse_unit_str(data: str) -> int:
    """将带有单位后缀的字符串转换为整数。
    支持的单位包括：
    - k (千，1024)
    - m (兆，1024^2)
    - g (吉，1024^3)

    如果输入字符串没有单位后缀，则直接将其视为整数。

    :param data: 包含数字和可选单位后缀的字符串
    :type data: str
    :return: 转换后的整数值
    :rtype: int
    """
    # 定义单位转换映射
    unit_map = {
        "k": 1024,
        "m": 1024**2,
        "g": 1024**3,  # 可选扩展：支持更多单位
    }

    # 将输入字符串转为小写以便统一处理
    data = data.lower()

    if data.isdigit():
        return int(data)
    # 遍历单位映射，尝试匹配单位后缀
    for unit, multiplier in unit_map.items():
        if data.endswith(unit):
            # 提取数字部分并进行计算
            num_part = data[: -len(unit)]
            return int(num_part) * multiplier
    raise ValueError(f"Invalid data format: {data}")


DBType = TypeVar("DBType")


class BaseTool(ABC, Generic[DBType]):
    """工具连接的基类，定义通用工具操作的抽象接口"""

    # 元数据
    type: Final[ProfileProvider] = ProfileProvider.UNKNOWN

    def __init__(self, config: SystemProfile):
        assert self.type != ProfileProvider.UNKNOWN, "数据库类型禁止为未知"
        self._config = config

        self.logger = getLogger(f"lorelm.db.{self.type.value}")

        self._client = self._get_client()
        self._after_init()

    @property
    def config(self):
        """数据库配置"""
        return self._config

    @abstractmethod
    def _get_client(self) -> DBType:
        """获取数据库客户端"""
        pass

    def _after_init(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
