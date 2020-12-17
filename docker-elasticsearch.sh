# Everything will be running when you see something like:
# "hello-nlp-elasticsearch_1  | INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:5055 (Press CTRL+C to quit)"

docker-compose -f docker-compose-elasticsearch.yml down
docker-compose -f docker-compose-elasticsearch.yml build
docker-compose -f docker-compose-elasticsearch.yml up