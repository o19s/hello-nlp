import os
import json

from typing import List, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from pydantic import BaseModel

from .auth import basic_auth
from .elastic import executor

from .skipchunkconnect import Connect
from .pipeline import Pipelines

app = FastAPI()

app.mount("/ui/", StaticFiles(directory="ui"), name="ui")

skipchunk = Connect(
    os.environ["ENGINE_USE_SSL"],
    os.environ["ENGINE_HOST"],
    os.environ["ENGINE_PORT"],
    os.environ["APP_NAME"],
    os.environ["ENGINE_NAME"],
    os.environ["DOCUMENTS_PATH"])

# Replace "*" to the list of your origins, e.g.
# origins = ["quepid.yourcompany.com", "localhost:8080"]
origins = "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('config.json','r') as fd:
    pipelines = Pipelines(json.load(fd))

@app.get('/')
async def index():
    return RedirectResponse("/ui/index.html")

@app.get('/environment')
async def show_environment() -> dict:
    """Shows the env-file configuration loaded for the Hello-NLP instance"""
    return {
        "NLP_USE_SSL": os.environ["NLP_USE_SSL"],
        "NLP_HOST": os.environ["NLP_HOST"],
        "NLP_PORT": os.environ["NLP_PORT"],
        "NLP_NAME": os.environ["NLP_NAME"],
        "NLP_ENGINE_NAME": os.environ["NLP_ENGINE_NAME"],
        "NLP_PATH": os.environ["NLP_PATH"],
        "WEB_CONCURRENCY":os.environ["WEB_CONCURRENCY"],
        "PROXY_USERNAME":os.environ["PROXY_USERNAME"]
        #,"PROXY_PASSWORD":os.environ["PROXY_PASSWORD"] <-- UNCOMMENT AT YOUR OWN RISK!
    }

# Suggest is our AJAX call for typeahead
@app.get('/suggest/{index_name}')
async def suggest(
    index_name: str, query: str
) -> dict:
    gq = skipchunk.graph_connect(index_name)
    suggestions = gq.suggestConcepts(query)
    return {'suggestions':suggestions}

# Cores is our AJAX call for core lists
@app.get('/indexes')
async def indexes() -> dict:
    indexes = skipchunk.gq.indexes()
    return {'indexes':indexes}

# Cores is our AJAX call for summarizing an index
@app.get('/indexes/{index_name}')
async def index_summarize(index_name: str) -> dict:
    gq = skipchunk.graph_connect(index_name)
    concepts,predicates = gq.summarize()
    return {'concepts':concepts,'predicates':predicates}

# Search the Solr core
@app.get('/solr/{index_name}/_select')
async def solrsearch(index_name: str, request: Request) -> dict:
    #print(request.query_params)
    iq = skipchunk.index_connect(index_name)
    query = request.query_params
    results,status = iq.search(query)
    return results,status

@app.get('/graph/{index_name}')
async def graph(index_name: str, subject: str) -> list:
    gq = skipchunk.graph_connect(index_name)
    """
    if "objects" in request.args.keys():
        objects = int(request.args["objects"])
    else:
        objects = 5
    if "branches" in request.args.keys():
        branches = int(request.args["branches"])
    else:
        branches = 10
    """
    objects = 5
    branches = 10
    tree = gq.graph(subject,objects=objects,branches=branches)
    return tree

@app.get('/analyze/{analyzer}')
async def analyze_text(analyzer: str, text: str) -> dict:
    try:
        res = {"output":str(pipelines.analyze(analyzer,text))}
    except e as ValueError:
        res = {"error":e}
    return res

class AnalyzeRequest(BaseModel):
    text:str

@app.post('/analyze/{analyzer}')
async def analyze_body(analyzer: str, body: AnalyzeRequest) -> dict:
    try:
        res = {"output":str(pipelines.analyze(analyzer,body.text))}
    except e as ValueError:
        res = {"error":e}
    return res

class EnrichRequest(BaseModel):
    doc:dict

@app.post('/enrich/')
async def enrich_document(body: EnrichRequest) -> dict:
    try:
        res = {"doc":str(pipelines.enrich(body.doc))}
    except ValueError as e:
        res = {"error":e}
    return res

## ====================
## Search Proxy
## ====================

class ProxyRequest(BaseModel):
    explain: bool
    from_: int
    size: int
    source: Optional[List[str]]
    query: Optional[dict]

    class Config:
        fields = {"from_": "from", "source": "_source"}

@app.get("/healthcheck")
async def health_check():
    """Health check"""
    return {"status": "OK"}

@app.post("/search/{index_name}")
async def search_proxy(
    index_name: str, body: ProxyRequest, username: str = Depends(basic_auth)
) -> dict:
    result = await executor.search(
        index_name,
        body.from_,
        body.size,
        body.explain,
        body.source,
        {"query": body.query} if body.query else None,
        None,
    )
    return result


@app.get("/explain/{index_name}")
async def explain_missing_documents(
    index_name: str,
    _source: str,
    q: str,
    size: int,
    username: str = Depends(basic_auth),
) -> dict:
    result = await executor.search(
        index_name,
        0,
        size,
        False,
        _source,
        None,
        q,
    )
    return result


@app.post("/explain/{index_name}/_doc/{doc_id}/_explain")
async def explain(
    index_name: str,
    doc_id: str,
    query: dict,
    username: str = Depends(basic_auth),
) -> dict:
    return await executor.explain(index_name, doc_id, query)
