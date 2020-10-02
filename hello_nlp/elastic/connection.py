# Copyright, 2020 AMBOSS GmbH
# Adopted from https://github.com/amboss-mededu/quepid-es-proxy/
# MIT License

import os
from distutils.util import strtobool

from elasticsearch import AsyncElasticsearch

from hello_nlp.exceptions import MissingEnvironmentVariable

_client = None

try:
    es_host = os.environ["ENGINE_HOST"]
    es_port = os.environ["ENGINE_PORT"]
    es_use_ssl = os.environ["ENGINE_USE_SSL"]
except KeyError as err:
    raise MissingEnvironmentVariable(f"Environment variable {err} is not set.")


async def get_connection() -> AsyncElasticsearch:
    """
    Returns a connection to the Elasticsearch.
    The connection is cached and reused. It is not
    creating a new connection every time.
    Required environment variables to create a connection:
        - ENGINE_HOST
        - ENGINE_PORT
        - ENGINE_USE_SSL
    """
    global _client
    if _client:
        return _client
    client = AsyncElasticsearch(
        hosts=[es_host],
        port=int(es_port),
        use_ssl=bool(strtobool(es_use_ssl)),
        verify_certs=True,
        http_compress=True,
        max_retries=5,
        retry_on_timeout=True,
    )
    _client = client
    return client
