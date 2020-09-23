#Adopted from https://github.com/amboss-mededu/quepid-es-proxy

run-tests:
	PYTHONPATH=`pwd` .venv/bin/pytest -W ignore tests/units --cov-report xml:cov.xml --cov .

run-elastic:
	PROXY_USERNAME="username" \
	PROXY_PASSWORD="password" \
	NLP_ENGINE_NAME="elasticsearch" NLP_USE_SSL=false NLP_HOST="localhost" NLP_PORT=9200 \
	NLP_NAME="osc-blog" NLP_PATH="./skipchunk_data" \
	WEB_CONCURRENCY=2 \
	uvicorn hello_nlp.main:app \
	--reload \
	--port 5050 \
	--host localhost \
	--use-colors \
	--access-log \

run-solr:
	PROXY_USERNAME="username" \
	PROXY_PASSWORD="password" \
	NLP_ENGINE_NAME="solr" NLP_USE_SSL=false NLP_HOST="localhost" NLP_PORT=8983 \
	NLP_NAME="osc-blog" NLP_PATH="./skipchunk_data" \
	WEB_CONCURRENCY=2 \
	uvicorn hello_nlp.main:app \
	--reload \
	--port 5050 \
	--host localhost \
	--use-colors \
	--access-log \
