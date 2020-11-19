# Copyright, 2020 AMBOSS GmbH, OpenSource Connections
# Adopted from https://github.com/amboss-mededu/quepid-es-proxy/
# MIT License

from typing import List, Optional

from .connection import get_connection

async def passthrough(index_name:str, body:dict):
    conn = await get_connection()

    query = {"query": body["query"]} if "query" in body else None

    payload = {
        "from_": body["from"],
        "size": body["size"],
        "explain": body["explain"],
        "_source": body["_source"]
    }

    body.pop("from")
    body.pop("size")
    body.pop("explain")
    body.pop("_source")

    payload["body"] = body

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

def index(index_name,document):
    pass
