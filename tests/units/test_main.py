import pytest
from asynctest import patch


@pytest.mark.parametrize(
    "query,expected_query",
    [(None, None), ({"day": "Friday"}, {"query": {"day": "Friday"}})],
)
async def test_search_proxy(environment, query, expected_query):

    from quepid_es_proxy import main

    with patch.object(
        main.executor, "search", return_value={"test": "passed"}
    ) as search_mock:
        result = await main.search_proxy(
            "big-index",
            body=main.ProxyRequst(
                **{"explain": True, "from": 3, "size": 7, "query": query}
            ),
        )

    assert result == {"test": "passed"}
    search_mock.assert_awaited_once_with(
        "big-index",
        3,
        7,
        True,
        None,
        expected_query,
        None,
    )


async def test_explain_missing_documents():
    from quepid_es_proxy import main

    with patch.object(
        main.executor, "search", return_value={"test": "passed"}
    ) as search_mock:
        result = await main.explain_missing_documents(
            index_name="index-123", _source="_id,title", q="title:Berlin", size=2
        )
    assert result == {"test": "passed"}
    search_mock.assert_awaited_once_with(
        "index-123", 0, 2, False, "_id,title", None, "title:Berlin"
    )


async def test_explain():
    from quepid_es_proxy import main

    with patch.object(
        main.executor, "explain", return_value={"test": "passed again!"}
    ) as explain_mock:
        result = await main.explain(
            index_name="index-123", doc_id="123_321", query={"match": "all"}
        )
    assert result == {"test": "passed again!"}
    explain_mock.assert_awaited_once_with("index-123", "123_321", {"match": "all"})
