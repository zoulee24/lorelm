import os.path
import re
from abc import ABC, abstractmethod
from typing import Iterable

import tiktoken  # OpenAI
from modelscope import snapshot_download
from tiktoken import Encoding as OpenAITokenizer
from tokenizers import Tokenizer  # Hugging Face

# import sentencepiece as spm # LLaMA

OPENAI_MODEL = re.compile(r"^(o[1,3,4].*|" r"gpt-\d[\.\d]+.*|text-embedding-.*)$")


class TokenPredicterBase(ABC):
    def __init__(self, tag: str):
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    @abstractmethod
    def encode(self, text: str) -> int:
        pass

    @abstractmethod
    def encode_batch(self, texts: Iterable[str]) -> Iterable[int]:
        pass


class HuggingfaceTokenPredict(TokenPredicterBase):
    def __init__(self, tag: str):
        cache_dir = snapshot_download(tag, allow_file_pattern="tokenizer.json")
        self._tk = Tokenizer.from_file(os.path.join(cache_dir, "tokenizer.json"))

    def encode(self, text: str) -> int:
        return len(self._tk.encode(text).ids)

    def encode_batch(self, texts: Iterable[str]) -> Iterable[int]:
        return (len(it.ids) for it in self._tk.encode_batch_fast(texts))


class OpenaiTokenPredict(TokenPredicterBase):
    def __init__(self, tag: str):
        super().__init__(tag)
        self._tk = tiktoken.encoding_for_model(tag)

    def encode(self, text: str) -> int:
        return len(self._tk.encode(text))

    def encode_batch(self, texts: Iterable[str]) -> Iterable[int]:
        return map(len, self._tk.encode_batch(texts))


class TokenPredicter(TokenPredicterBase):
    def __init__(self, tag: str):
        super().__init__(tag)
        matched = OPENAI_MODEL.match(tag)
        if matched is not None:
            self._imp = OpenaiTokenPredict(tag)
        else:
            self._imp = HuggingfaceTokenPredict(tag)
        # self.encode = self._imp.encode
        # self.encode_batch = self._imp.encode_batch

    def encode(self, text: str) -> int:
        return self._imp.encode(text)

    def encode_batch(self, texts: Iterable[str]) -> Iterable[int]:
        return self._imp.encode_batch(texts)


if __name__ == "__main__":
    tag = "BAAI/bge-m3"
    m = TokenPredicter(tag)
    res = m.encode("测试一下！")
    print(type(res), res)
    res = m.encode_batch(["测试一下！"] * 10)
    print(type(res), res)
