from typing import List, Optional

from .connection import get_connection


async def search(
    index_name: str,
    from_: int,
    size: int,
    explain: bool = False,
    source: Optional[List[str]] = None,
    query: Optional[str] = None,
    q: Optional[str] = None,
):
    conn = await get_connection()
    payload = {
        "from_": from_,
        "size": size,
        "explain": explain,
        "_source": source,
        "body": query,
        "q": q,
    }
    r = conn.search(
        index=index_name,
        **payload,
    )
    return await r


async def explain(
    index_name: str,
    document_id: str,
    query: str,
):
    conn = await get_connection()
    return await conn.explain(index_name, document_id, query)
