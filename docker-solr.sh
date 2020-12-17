# Everything will be running when you see something like:
# "hello-nlp-solr_1  | INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:5050 (Press CTRL+C to quit)"

docker-compose -f docker-compose-solr.yml down
docker-compose -f docker-compose-solr.yml build
docker-compose -f docker-compose-solr.yml up