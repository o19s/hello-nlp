uvicorn hello_nlp.main:app \
--reload \
--port 5055 \
--host localhost \
--use-colors \
--access-log \
--env-file elasticsearch.conf