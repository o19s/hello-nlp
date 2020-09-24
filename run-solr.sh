uvicorn hello_nlp.main:app \
--reload \
--port 5050 \
--host localhost \
--use-colors \
--access-log \
--env-file solr.conf