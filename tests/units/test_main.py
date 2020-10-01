import pytest
from asynctest import patch


@pytest.mark.parametrize("engine_name", ["elastic","elasticsearch","es"])
async def test_explain_missing_documents(monkeypatch, engine_name):
    monkeypatch.setenv("ENGINE_NAME", engine_name)

    from hello_nlp import main

    with patch.object(
        main.elastic_executor, "passthrough", return_value={"test": "passed"}
    ) as search_mock:
        result = await main.explain_missing_documents(
            index_name="index-123", _source="_id,title", q="title:Berlin", size=2
        )
    assert result == {"test": "passed"}
    search_mock.assert_awaited_once_with(
        "index-123", 0, 2, False, "_id,title", None, "title:Berlin"
    )


async def test_explain():

    from hello_nlp import main

    with patch.object(
        main.elastic_executor, "explain", return_value={"test": "passed again!"}
    ) as explain_mock:
        result = await main.explain(
            index_name="index-123", doc_id="123_321", query={"match": "all"}
        )
    assert result == {"test": "passed again!"}
    explain_mock.assert_awaited_once_with("index-123", "123_321", {"match": "all"})
