import math
import os.path
import re
from copy import deepcopy
from logging import getLogger
from typing import Iterable, Optional

import datrie
from hanziconv import HanziConv
from jieba import Tokenizer as JiebaTokenizer

from ...utils.common import get_root_dir


class Tokenizer:
    _DENOMINATOR = 1000

    def __init__(self):
        self.logger = getLogger("lorelm.nlp.tokenizer")
        # self._tokenizer = JiebaTokenizer(get_root_dir("resources/nlp/huqie.txt"))
        self._tokenizer = JiebaTokenizer()
        self._tokenizer.initialize()
        tokenizer_file = get_root_dir("resources/nlp/huqie.txt")
        self.__trie = self.__load_trie(tokenizer_file)

    def __load_trie(self, file_path: str):
        dict_file_cache = file_path + ".cache"
        if os.path.exists(dict_file_cache):
            trie = datrie.Trie.load(dict_file_cache)
        else:
            from string import printable

            self.logger.info(f"Build trie from {file_path}, it may take a while")
            trie = datrie.Trie(printable)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        line = re.sub(r"[\r\n]+", "", line)
                        line = re.split(r"[ \t]", line)
                        k = self.__key(line[0])
                        F = int(math.log(float(line[1]) / self._DENOMINATOR) + 0.5)
                        if k not in trie or trie[k][0] < F:
                            trie[self.__key(line[0])] = (F, line[2])
                        trie[self.__rkey(line[0])] = 1

                trie.save(dict_file_cache)
                self.logger.info(
                    f"Build trie {file_path} success, save cache to {dict_file_cache}"
                )
            except Exception as e:
                self.logger.exception(f"Build trie {file_path} failed, {e}")
                raise RuntimeError(f"Build trie {file_path} failed, {e}") from e
        return trie

    def tokenize(self, text: str) -> Iterable[str]:
        text = re.sub(r"\W+", " ", text)
        text = self.full2half(text).lower()
        text = self.tradi2simp(text)
        return (it for it in self._tokenizer.cut(text) if it.strip())

    def fine_grained_tokenize(self, texts: Iterable[str]) -> list[str]:
        res = []
        for tk in texts:
            if len(tk) < 3 or re.match(r"[0-9,\.-]+$", tk):
                res.append(tk)
                continue
            tks_list = []
            if len(tk) > 10:
                tks_list.append(tk)
            else:
                self.__dfs(tk, 0, [], tks_list)
            if len(tks_list) < 2:
                res.append(tk)
                continue
            stk = self.__sort_tks(tks_list)[1][0]
            if len(stk) == len(tk):
                stk = tk
            else:
                if re.match(r"[a-z\.-]+$", tk):
                    for t in stk:
                        if len(t) < 3:
                            stk = tk
                            break
                    else:
                        stk = " ".join(stk)
                else:
                    stk = " ".join(stk)

            res.append(stk)

        return res

    @staticmethod
    def tradi2simp(line: str) -> str:
        return HanziConv.toSimplified(line)

    @staticmethod
    def full2half(line: str) -> str:
        full_to_half = str.maketrans(
            {0x3000: 0x0020, **{i: i - 0xFEE0 for i in range(0xFF01, 0xFF5F)}}
        )
        return line.translate(full_to_half)

    def __dfs(
        self,
        chars: str,
        s: int,
        preTks: list[tuple[str, tuple[int, str]]],
        tks_list: list[tuple[str, tuple[int, str]]],
        _depth: int = 0,
        _memo: Optional[dict] = None,
    ):
        if _memo is None:
            _memo = dict()
        MAX_DEPTH = 10
        if _depth > MAX_DEPTH:
            if s < len(chars):
                copy_pretks = deepcopy(preTks)
                remaining = "".join(chars[s:])
                copy_pretks.append((remaining, (-12, "")))
                tks_list.append(copy_pretks)
            return s

        state_key = (s, tuple(tk[0] for tk in preTks)) if preTks else (s, None)
        if state_key in _memo:
            return _memo[state_key]

        res = s
        if s >= len(chars):
            tks_list.append(preTks)
            _memo[state_key] = s
            return s
        if s < len(chars) - 4:
            is_repetitive = True
            char_to_check = chars[s]
            for i in range(1, 5):
                if s + i >= len(chars) or chars[s + i] != char_to_check:
                    is_repetitive = False
                    break
            if is_repetitive:
                end = s
                while end < len(chars) and chars[end] == char_to_check:
                    end += 1
                mid = s + min(10, end - s)
                t = "".join(chars[s:mid])
                k = self.__key(t)
                copy_pretks = deepcopy(preTks)
                if k in self.__trie:
                    copy_pretks.append((t, self.__trie[k]))
                else:
                    copy_pretks.append((t, (-12, "")))
                next_res = self.__dfs(
                    chars, mid, copy_pretks, tks_list, _depth + 1, _memo
                )
                res = max(res, next_res)
                _memo[state_key] = res
                return res

        S = s + 1
        if s + 2 <= len(chars):
            t1 = "".join(chars[s : s + 1])
            t2 = "".join(chars[s : s + 2])
            if self.__trie.has_keys_with_prefix(
                self.__key(t1)
            ) and not self.__trie.has_keys_with_prefix(self.__key(t2)):
                S = s + 2
        if (
            len(preTks) > 2
            and len(preTks[-1][0]) == 1
            and len(preTks[-2][0]) == 1
            and len(preTks[-3][0]) == 1
        ):
            t1 = preTks[-1][0] + "".join(chars[s : s + 1])
            if self.__trie.has_keys_with_prefix(self.__key(t1)):
                S = s + 2

        for e in range(S, len(chars) + 1):
            t = "".join(chars[s:e])
            k = self.__key(t)
            if e > s + 1 and not self.__trie.has_keys_with_prefix(k):
                break
            if k in self.__trie:
                pretks = deepcopy(preTks)
                pretks.append((t, self.__trie[k]))
                res = max(
                    res, self.__dfs(chars, e, pretks, tks_list, _depth + 1, _memo)
                )

        if res > s:
            _memo[state_key] = res
            return res

        t = "".join(chars[s : s + 1])
        k = self.__key(t)
        copy_pretks = deepcopy(preTks)
        if k in self.__trie:
            copy_pretks.append((t, self.__trie[k]))
        else:
            copy_pretks.append((t, (-12, "")))
        result = self.__dfs(chars, s + 1, copy_pretks, tks_list, _depth + 1, _memo)
        _memo[state_key] = result
        return result

    # def __score(self, tfts):
    #     B = 30
    #     F, L, tks = 0, 0, []
    #     for tk, (freq, tag) in tfts:
    #         F += freq
    #         L += 0 if len(tk) < 2 else 1
    #         tks.append(tk)
    #     # F /= len(tks)
    #     L /= len(tks)
    #     return tks, B / len(tks) + L + F

    def __score(
        self, tfts: list[tuple[str, tuple[int, str]]]
    ) -> tuple[list[str], float]:
        """计算分词方案的得分"""
        B = 30  # 基础分数
        total_freq = 0
        long_word_count = 0
        tokens = []

        for token, (freq, _) in tfts:
            total_freq += freq
            if len(token) >= 2:
                long_word_count += 1
            tokens.append(token)

        # 计算各项指标
        avg_freq = total_freq / len(tfts)
        long_word_ratio = long_word_count / len(tfts)

        # 综合得分：基础分/词数 + 长词比例 + 平均频率
        score = B / len(tfts) + long_word_ratio + avg_freq
        return tokens, score

    def __sort_tks(self, tks_list: list[tuple[str, tuple[int, str]]]):
        return sorted(
            (self.__score(tfts) for tfts in tks_list),  # 每个元素只调用一次 __score
            key=lambda x: x[1],
            reverse=True,
        )

    def __key(self, line: str) -> str:
        """生成前缀树键"""
        return str(line.lower().encode("utf-8"))[2:-1]

    def __rkey(self, line: str) -> str:
        """生成反向前缀树键"""
        return str(("DD" + (line[::-1].lower())).encode("utf-8"))[2:-1]

    def freq(self, tk) -> int:
        k = self.__key(tk)
        if k not in self.__trie:
            return 0
        return int(math.exp(self.__trie[k][0]) * self._DENOMINATOR + 0.5)

    def tag(self, tk) -> str:
        k = self.__key(tk)
        if k not in self.__trie:
            return ""
        return self.__trie[k][1]


if __name__ == "__main__":
    tokenizer = Tokenizer()
    s = "基本上说为什么发多少i发动机输出你哦圣诞节京东集团2023年年报里面第1季度利润最高的部门是哪一个？"

    # print(tokenizer._tokenizer.total)

    ss = list(tokenizer.tokenize(s))

    print(" ".join(ss))
    print(" ".join(tokenizer.fine_grained_tokenize(ss)))
