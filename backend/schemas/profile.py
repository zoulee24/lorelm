from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfileType(StrEnum):
    """配置类型"""

    SQL = "sql"
    NoSQL = "nosql"
    OSS = "oss"
    Vector = "vector"
    MessageQueue = "mq"


class ProfileProvider(StrEnum):
    """配置提供者"""

    UNKNOWN = "unknown"

    # 关系型数据库
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SQLITE = "sqlite"

    # NoSQL
    Redis = "redis"
    Valkey = "valkey"

    # OSS
    AliYunOss = "aliyun_oss"
    Minio = "minio"
    RustFS = "rustfs"

    # 向量数据库
    ElasticSearch = "elasticsearch"
    PGVector = "pgvector"

    # 图数据库
    NEPTUNE = "neptune"
    NEO4J = "neo4j"

    # 消息队列
    RABBITMQ = "rabbitmq"


class SystemProfile(BaseModel):
    name: str = Field(description="配置名称")
    type: ProfileType = Field(description="配置类型")
    provider: ProfileProvider = Field(description="服务商")

    host: str = Field(description="服务地址")
    port: int = Field(ge=0, le=65535, description="服务端口")

    username: Optional[str] = Field(description="用户名")
    password: Optional[str] = Field(description="密码")

    db: Optional[str] = Field(None, description="数据库")
    extra: Dict[str, Any] = Field(default_factory=dict, description="额外配置")

    model_config = ConfigDict(from_attributes=True)
