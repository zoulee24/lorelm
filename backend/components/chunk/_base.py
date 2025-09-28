from abc import ABC, abstractmethod
from logging import getLogger
from typing import Generic

from typing_extensions import TypeVar

from ...schemas.components import ChunkingConfig, DocumentDict
from ...utils.nlp import Tokenizer
from ...utils.token_predict import TokenPredicter

ConfigType = TypeVar("ConfigType", bound="ChunkingConfig", default="ChunkingConfig")


class ChunkingBase(ABC, Generic[ConfigType]):
    """分块基类"""

    def __init__(self, config: ConfigType):
        self.tokenizer = Tokenizer()
        self.embed_predict = TokenPredicter(config["embed_tag"])
        self._config = config
        self.logger = getLogger("lorelm.components.chunk")

    @abstractmethod
    def __call__(self, content) -> list[DocumentDict]:
        """分块"""
        pass

    @property
    def config(self) -> ConfigType:
        """配置"""
        return self._config
