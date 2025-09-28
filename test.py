# import os

# from dotenv import load_dotenv

# load_dotenv()

# from omni_llm import async_embedding_factory
# from sqlalchemy import desc, func, or_, select

# # from pgvector.sqlalchemy import to
# from backend.components import chunking
# from backend.dependencies.database import db_deinit, db_init
# from backend.models.character import Document
# from backend.utils.nlp import FullTextQueryer, Tokenizer
# from backend.utils.vector import get_vdb_with

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
# OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL")
# OPENAI_EMBED_DIMS = int(os.getenv("OPENAI_EMBED_DIMS"))
# assert OPENAI_EMBED_DIMS == 1024, "OPENAI_EMBED_DIMS must be 1024"


# async def insert():
#     await db_init()
#     with open("哈利·波特.md", "r") as f:
#         content = f.read()
#     docs = await chunking("naive", content, 1)
#     async with get_vdb_with() as vdb:
#         if not await vdb.index_exists("lorelm"):
#             await vdb.index_create("lorelm", OPENAI_EMBED_DIMS)
#         await vdb.doc_batch_insert("lorelm", docs)
#     await db_deinit()


# async def search(query: str):
#     # await db_init()
#     embed_md = async_embedding_factory("siliconflow")(
#         OPENAI_EMBED_MODEL,
#         -1,
#         OPENAI_EMBED_DIMS,
#         OPENAI_BASE_URL,
#         OPENAI_API_KEY,
#     )
#     top_k = 1024
#     query_vector: list[float] = (await embed_md.encode([query])).v[0].tolist()
#     # tokenizer = Tokenizer()
#     # query_ltks = list(tokenizer.tokenize(query))
#     # query_ltks_sm = tokenizer.fine_grained_tokenize(query_ltks)
#     # query_vector = (await embed_md.encode(query_ltks_sm)).v[0].tolist()
#     quweyer = FullTextQueryer()
#     qs, kws = quweyer.question(query)
#     async with get_vdb_with() as vdb:
#         results = await vdb.search(
#             "lorelm", docs_id=1, query_string=qs, query_vector=query_vector, top_k=top_k
#         )
#         for result in results:
#             print(result.content)

#     # await db_deinit()


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(insert())
#     # asyncio.run(search("莉莉和魔法部关系怎么样"))
import os

print(os.path.splitext("a.pdf"))
