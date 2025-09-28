import re
from operator import itemgetter
from typing import Union

import jieba.analyse

from .synonym import Dealer as SynonymDealer
from .tokenizer import Tokenizer


class FullTextQueryer:
    MAX_KEYWORDS = 32

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.syn = SynonymDealer()
        self.tf_idf = jieba.analyse.TFIDF()

    @staticmethod
    def rmWWW(txt):
        patts = (
            # 原有模式...
            (
                r"(有|存在)*(\d+|多少|几|几多)(个|块|名|只|片|年|月|天|小时|分钟|秒|公里|米|厘米|毫米|吨|千克|克|斤|两|升|毫升)",
                "",
            ),
            (r"(第|排行|排在)(\d+|一|二|三|四|五|六|七|八|九|十)(位|名)", ""),
            (r"(现在|目前|当前|以前|以后|将来|过去|未来|最近|最早|最晚)是*", ""),
            (r"(\d{4}年)*(\d+月)*(\d+日)*", ""),
            (r"(上午|下午|晚上|凌晨|早晨|中午|傍晚)(\d+点)*", ""),
            (
                r"(在|位于|处在|坐落在|处于|在|靠近|临近|旁边|附近|周围|周围地区|周围区域)哪里*",
                "",
            ),
            (
                r"(东|南|西|北|东南|东北|西南|西北|里面|外面|内部|外部|中心|边缘|边界)边*",
                "",
            ),
            (r"(最|更|比较|十分|非常|特别|极其|相当|很|挺|蛮|有点|稍微)是*", ""),
            (r"(比|跟|与|和|同)(.*)相比*", ""),
            (r"(因为|由于|因此|所以|结果|导致|引起|造成|使得|以便|为了|目的是)是*", ""),
            (r"(不|没|无|非|未|别|不要|不用|不必|无需)是*", ""),
            (r"(如果|假如|假设|要是|倘若|即使|哪怕|无论|不管)是*", ""),
            (r"(指|叫做|称为|名叫|被誉为|堪称|算是|当作|当成|视为|看作)是*", ""),
            (r"(属于|归于|列入|划为|算作|当作|当成)什么*类别*", ""),
            (r"(完全|基本|大致|大概|大约|差不多|基本上|完全地|彻底地|充分地)是*", ""),
            (
                r"(以及|或者|还是|或是|即|也就是说|换句话说|例如|比如|譬如|像|如同|犹如)是*",
                "",
            ),
            # 英文扩展
            (
                r"(^| )(can|could|may|might|must|shall|should|will|would|can't|couldn't|mustn't|shouldn't|won't) ",
                " ",
            ),
            (
                r"(^| )(about|above|across|after|against|along|among|around|before|behind|below|beneath|beside|between|beyond|during|except|from|into|onto|through|throughout|till|toward|under|until|upon|within|without) ",
                " ",
            ),
        )
        otxt = txt
        for r, p in patts:
            txt = re.sub(r, p, txt, flags=re.IGNORECASE)
        if not txt:
            txt = otxt
        return txt

    def question(self, q: str) -> tuple[str, list[str]]:
        tms = []
        keywords: list[str] = []

        # 去除符号、繁体转简体、全角转半角
        q = re.sub(
            r"[ :|\r\n\t,，。？?/`!！&^%%()\[\]{}<>]+",
            " ",
            self.tokenizer.tradi2simp(self.tokenizer.full2half(q.lower())),
        ).strip()
        # 去除问题词语
        q = self.rmWWW(q)

        # 计算权重
        weights = self.tf_idf.extract_tags(q, withWeight=True)

        # 句子级别同义词
        syns = self.syn.lookup(q)
        if syns and len(keywords) < self.MAX_KEYWORDS:
            keywords.extend(syns)

        for tk, w in weights:
            if need_fine_grained_tokenize(tk):
                sm = self.tokenizer.fine_grained_tokenize(tuple(tk))
            else:
                sm = []
            sm = (
                re.sub(
                    r"[ ,\./;'\[\]\\`~!@#$%\^&\*\(\)=\+_<>\?:\"\{\}\|，。；‘’【】、！￥……（）——《》？：“”-]+",
                    "",
                    m,
                )
                for m in sm
            )
            sm = (subSpecialChar(m) for m in sm if len(m) > 1)
            sm = [m for m in sm if len(m) > 1]

            if len(keywords) < self.MAX_KEYWORDS:
                keywords.append(re.sub(r"[ \\\"']+", "", tk))
                keywords.extend(sm)

            # 词组级别同义词
            tk_syns = (subSpecialChar(s) for s in self.syn.lookup(tk))
            tk_syns = [s for s in tk_syns if s]
            if len(keywords) < self.MAX_KEYWORDS:
                keywords.extend(tk_syns)
            tk_syns = self.tokenizer.fine_grained_tokenize(tk_syns)
            tk_syns = [f'"{s}"' if s.find(" ") > 0 else s for s in tk_syns]

            if len(keywords) >= self.MAX_KEYWORDS:
                break

            tk = subSpecialChar(tk)
            if tk.find(" ") > 0:
                tk = '"%s"' % tk
            if tk_syns:
                tk = f"({tk} OR (%s)^0.2)" % " ".join(tk_syns)
            if sm:
                tk = f'{tk} OR "%s" OR ("%s"~2)^0.5' % (" ".join(sm), " ".join(sm))
            if tk.strip():
                tms.append((tk, w))
        tms = " ".join([f"({t})^{round(w, 3)}" for t, w in tms])

        if len(weights) > 1:
            tms += ' ("%s"~2)^1.5' % " ".join(self.tokenizer.tokenize(q))
        return tms, keywords

    def token_similarity(
        self, q: str | list[str], targets: list[str | list[str]]
    ) -> list[float]:
        if not targets:
            return list()
        w_qtwt = self._extract_tags(q)
        return [self.similarity(w_qtwt, t) for t in targets]

    def similarity(
        self, qtwt: Union[dict[str, float], str], dtwt: str | list[str]
    ) -> float:
        w_qtwt = (
            {k: v for k, v in self._extract_tags(qtwt).items()}
            if isinstance(qtwt, str)
            else qtwt
        )
        w_dtwt = {k: v for k, v in self._extract_tags(dtwt).items()}

        # 使用集合快速查找共同词汇
        q = sum(w_dtwt.values())
        if q == 0:
            return 0
        s = sum(w_qtwt[k] for k in w_qtwt if k in set(w_dtwt.keys()))
        return s / q

    def _extract_tags(self, texts: str | list[str], topK: int = 20) -> dict[str, float]:
        if isinstance(texts, str):
            w_qtwt = {k: v for k, v in self.tf_idf.extract_tags(texts, withWeight=True)}
        elif isinstance(texts, list):
            freq = {}
            for w in texts:
                if len(w.strip()) < 2 or w.lower() in self.tf_idf.stop_words:
                    continue
                freq[w] = freq.get(w, 0.0) + 1.0
            total = sum(freq.values())
            for k in freq:
                freq[k] *= self.tf_idf.idf_freq.get(k, self.tf_idf.median_idf) / total

            tags = sorted(freq.items(), key=itemgetter(1), reverse=True)[:topK]
            w_qtwt = {k: v for k, v in tags}
        else:
            raise TypeError("q must be a string or a list")
        return w_qtwt


def subSpecialChar(line: str) -> str:
    return re.sub(r"([:\{\}/\[\]\-\*\"\(\)\|\+~\^])", r"\\\1", line).strip()


def need_fine_grained_tokenize(tk):
    if len(tk) < 3:
        return False
    if re.match(r"[0-9a-z\.\+#_\*-]+$", tk):
        return False
    return True
