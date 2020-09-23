# Hello-NLP




# Quepid Elasticsearch Proxy
## Elasticsearch proxy for Quepid. 
A lot of Quepid users are surprised by the fact that Quepid
works with Elasticsearch directly from the browser. Elasticsearch are 
rarely available publicly or can be tunnneled to the labeller's computer.

`Quepid Elasticsearch Proxy` can be deployed next to your `Quepid` and can proxy requests to Elasticsearch. The proxy is protected with basic auth.


## Run with Docker
The image of the proxy is publicly available on [https://quay.io/amboss-mededu/quepid_es_proxy]().
To run the proxy docker execute
```bash
docker run \
-e "PROXY_USERNAME=username_is_here" \
-e "PROXY_PASSWORD=password_is_here" \
-e "ES_HOST=example-elasticsearch-domain.eu-west-1.es.amazonaws.com" \
-e "ES_PORT=443" \
-e "ES_USE_SSL=true" \
-e "WEB_CONCURRENCY=2" \
-p 5000:5000 \
quay.io/amboss-mededu/quepid_es_proxy
```
The proxy is now available with basic auth now on `http://username_is_here:password_is_here@localhost:5000/`. 
Use this address in Quepid insted of Elasticsearch.

If you run Elasticsearch locally in Docker, use Docker DNS in `ES_HOST`. 
You might also need to specify a Docker network in which Elasticsearch is running.
```bash
docker run \
-e "PROXY_USERNAME=username_is_here" \
-e "PROXY_PASSWORD=password_is_here" \
-e "ES_HOST=elasticsearch_docker_name" \
-e "ES_PORT=9200" \
-e "ES_USE_SSL=false" \
-e "WEB_CONCURRENCY=2" \
-p 5000:5000 \
--network="elasticsearch-docker-network" \
quay.io/amboss-mededu/quepid_es_proxy
```

## Run locally with Python virtual environment.

Proxy uses Python 3.8.

First prepare a virtual environment `make prepare-env`.
The proxy will be available with the default credentials on
`http://lab_user:jhHB73bYBKk6G^@localhost:5000/`.

To run the proxy locally execute `make run-service`. Modify `PROXY_USERNAME` and `PROXY_PASSWORD` environment variables in the `run-server` make target if you need.

## Development
### make doit
To sort imports, format the code in the consistent way and execute `flake8` and `mypy` checks run `make doit`.
### Formatting
The code base is formatted with [https://github.com/psf/black](black).
### Imports
Imports are sorted with [https://github.com/PyCQA/isort](isort).
### Pre-commit hooks.
1. Install pre-commit. On Mac use `brew install pre-commit`, on Linux `pip install pre-commit`. 
2. Install hooks `pre-commit install`.

