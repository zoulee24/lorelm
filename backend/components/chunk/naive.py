import re

from ...schemas.components.chunk import DocumentCreateDict
from ...utils.common import get_unix_timestamp
from ._base import ChunkingBase


class ChunkingNaive(ChunkingBase):
    def __call__(self, content: str) -> list[DocumentCreateDict]:
        if not content:
            self.logger.warning(f"file do not contain anything")
            return []
        chunk_size = self.config["chunk_size"]

        no_table_content, tables = self._table_extract(content)
        self.logger.info(f"提取表格 {len(tables)} 个")

        wait_for_process = [it for it in no_table_content.split("\n") if it]
        batch_token_cost = self.embed_predict.encode_batch(wait_for_process)

        sections: list[str] = []

        for token_cost, section in zip(batch_token_cost, wait_for_process):
            if token_cost > 3 * chunk_size:
                sections.append(section[: int(len(section) / 2)])
                sections.append(section[int(len(section) / 2) :])
            else:
                if section.strip().find("#") == 0:
                    sections.append(section)
                elif sections and sections[-1][0].strip().find("#") == 0:
                    sec_ = sections.pop(-1)
                    sections.append(sec_ + "\n" + section)
                else:
                    sections.append(section)

        chunks = self._merge_chunking(sections)
        self.logger.info(f"分块 {len(chunks)} 个")
        docs = [self.text_tokenize(chunk) for chunk in chunks if chunk.strip()]

        number_of_tokens = list(self.embed_predict.encode_batch(tables))
        for table, number_of_token in zip(tables, number_of_tokens):
            docs.extend(self.table_tokenize(table, number_of_token, False))
        return docs

    def _table_extract(self, content: str):
        tables: list[str] = []

        md_tables = BORDER_TABLE_PARTERN.findall(content)
        if md_tables:
            tables.extend(md_tables)
            content = BORDER_TABLE_PARTERN.sub("", content)

        html_tables = HTML_TABLE_PARTERN.findall(content)
        if html_tables:
            tables.extend(html_tables)
            content = HTML_TABLE_PARTERN.sub("", content)
        return content, tables

    def _merge_chunking(self, sections: list[str]) -> list[str]:
        if not sections:
            return []
        chunk_size = self.config["chunk_size"]
        overlap_size = self.config["overlap_size"]
        cks = [""]
        tk_nums = [0]

        def add_chunk(text: str, tnum: int):
            nonlocal cks, tk_nums
            # Ensure that the length of the merged chunk does not exceed chunk_token_num
            if tk_nums[-1] > chunk_size:
                cks.append(text)
                tk_nums.append(tnum)
            else:
                cks[-1] += text
                tk_nums[-1] += tnum

        number_of_tokens = self.embed_predict.encode_batch(sections)
        pattern = get_delimiters("\n。；！？")
        for number_of_token, section in zip(number_of_tokens, sections):
            # 避免一个段落太大超token
            if number_of_token > 3 * chunk_size:
                split_sec = re.split(r"(%s)" % pattern, section, flags=re.DOTALL)
                sub_number_of_tokens = self.embed_predict.encode_batch(split_sec)
                for sub_sec, sub_n_of_token in zip(split_sec, sub_number_of_tokens):
                    if re.match(f"^{pattern}$", sub_sec):
                        continue
                    add_chunk(sub_sec, sub_n_of_token)
            else:
                add_chunk(section, number_of_token)

        return cks

    def text_tokenize(self, content: str) -> DocumentCreateDict:
        """文本分词

        :param content: 文档原文
        :type content: str
        :return: 增加分词后的文档
        :rtype: DocumentCreateDict
        """
        content_ltks = list(
            self.tokenizer.tokenize(
                re.sub(
                    r"</?(table|td|caption|tr|th|tbody)( [^<>]{0,12})?>", " ", content
                )
            )
        )
        content_sm_ltks = self.tokenizer.fine_grained_tokenize(content_ltks)
        timestamp = get_unix_timestamp()
        return DocumentCreateDict(
            content=content,
            content_ltks=" ".join(content_ltks),
            content_sm_ltks=" ".join(content_sm_ltks),
            create_at=timestamp,
            update_at=timestamp,
            delete_at=None,
        )

    def table_tokenize(
        self,
        table: str,
        number_of_token: int,
        is_english: bool,
        batch_size: int = 8,
    ) -> list[DocumentCreateDict]:
        docs = []
        table = table.strip()
        if not table:
            return docs
        # 解决单个表格太大的问题
        # TODO：大表格分隔待优化
        if number_of_token > 8096:
            rows = table.split("<tr>")
            sub_number_of_tokens = self.embed_predict.encode_batch(rows)
            tbs = [[]]
            row_token = 0
            for row, sub_number_of_token in zip(rows, sub_number_of_tokens):
                row_token += sub_number_of_token
                tbs[-1].append(row)
                if row_token > 4096:
                    tbs.append([])
                    row_token = 0
            for tb in tbs:
                row = "<tr>".join(tb)
                if not row.endswith("</tbody></table>"):
                    row += "</tbody></table>"
                if not row.startswith("<table><tbody>"):
                    row = f"<table><tbody>{row}"
                docs.append(self.text_tokenize(row))
        else:
            docs.append(self.text_tokenize(table))
        return docs


# markdown 格式 表格
BORDER_TABLE_PARTERN = re.compile(
    r"""
    (?:\n|^)                     
    (?:\|.*?\|.*?\|.*?\n)        
    (?:\|(?:\s*[:-]+[-| :]*\s*)\|.*?\n) 
    (?:\|.*?\|.*?\|.*?\n)+
    """,
    re.VERBOSE,
)
# html 格式 表格
HTML_TABLE_PARTERN = re.compile(
    r"""
    (?:\n|^)
    \s*
    (?:
        # case1: <html><body><table>...</table></body></html>
        (?:<html[^>]*>\s*<body[^>]*>\s*<table[^>]*>.*?</table>\s*</body>\s*</html>)
        |
        # case2: <body><table>...</table></body>
        (?:<body[^>]*>\s*<table[^>]*>.*?</table>\s*</body>)
        |
        # case3: only<table>...</table>
        (?:<table[^>]*>.*?</table>)
    )
    \s*
    (?=\n|$)
    """,
    re.VERBOSE | re.DOTALL | re.IGNORECASE,
)


def get_delimiters(delimiters: str):
    dels = []
    s = 0
    for m in re.finditer(r"`([^`]+)`", delimiters, re.I):
        f, t = m.span()
        dels.append(m.group(1))
        dels.extend(list(delimiters[s:f]))
        s = t
    if s < len(delimiters):
        dels.extend(list(delimiters[s:]))

    dels.sort(key=lambda x: -len(x))
    dels = [re.escape(d) for d in dels if d]
    dels = [d for d in dels if d]
    dels_pattern = "|".join(dels)

    return dels_pattern
