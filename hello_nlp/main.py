import os
import json
import urllib 

from typing import List, Optional

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from pydantic import BaseModel

from .auth import basic_auth
from .elastic import executor as elastic_executor
from .solr import executor as solr_executor

from .skipchunkconnect import Connect
from .pipeline import Pipelines

from .storage import saveDocument,indexableDocuments

app = FastAPI()

app.mount("/ui/", StaticFiles(directory="ui"), name="ui")

skipchunk = Connect(
    os.environ["ENGINE_USE_SSL"],
    os.environ["ENGINE_HOST"],
    os.environ["ENGINE_PORT"],
    os.environ["APP_NAME"],
    os.environ["ENGINE_NAME"],
    os.environ["DOCUMENTS_PATH"])

if os.environ["ENGINE_NAME"] in ["solr"]:
    executor = solr_executor
elif os.environ["ENGINE_NAME"] in ["elastic","elasticsearch","es"]:
    executor = elastic_executor

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
    config_json = json.load(fd)
    pipelines = Pipelines(config_json)
    #pipelines = {}

@app.get('/')
async def index():
    return RedirectResponse("/ui/index.html")

@app.get('/environment')
async def show_environment() -> dict:
    """Shows the env-file configuration loaded for the Hello-NLP instance"""
    return {
        "ENGINE_USE_SSL": os.environ["ENGINE_USE_SSL"],
        "ENGINE_HOST": os.environ["ENGINE_HOST"],
        "ENGINE_PORT": os.environ["ENGINE_PORT"],
        "APP_NAME": os.environ["APP_NAME"],
        "ENGINE_NAME": os.environ["ENGINE_NAME"],
        "DOCUMENTS_PATH": os.environ["DOCUMENTS_PATH"],
        "WEB_CONCURRENCY":os.environ["WEB_CONCURRENCY"],
        "PROXY_USERNAME":os.environ["PROXY_USERNAME"]
        #,"PROXY_PASSWORD":os.environ["PROXY_PASSWORD"] <-- UNCOMMENT AT YOUR OWN RISK!
    }

@app.get('/pipeline')
async def show_pipeline() -> dict:
    """Shows the config.json pipeline loaded for the Hello-NLP instance"""
    return config_json

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

@app.get('/analyzers')
async def analyzers() -> dict:
    try:
        #data = [{'name':a} for a in pipelines.analyzers.keys()]
        data = list(pipelines.analyzers.keys())
        res = {'data':data}
    except ValueError as e:
        print(e)
        res = {'error':e}
    return res

@app.get('/analyze/{analyzer}')
async def analyze_text(analyzer: str, text: str, debug:bool=False) -> dict:
    try:
        data, data_debug = pipelines.analyze(analyzer,text,debug=debug)
        res = {"data":str(data),"debug":data_debug}
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res

class AnalyzeRequest(BaseModel):
    text:str

@app.post('/analyze/{analyzer}')
async def analyze_body(analyzer: str, body: AnalyzeRequest) -> dict:
    try:
        data, data_debug = pipelines.analyze(analyzer,body.text,debug=debug)
        res = {"data":str(data),"debug":data_debug}
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res


class IndexableDocument(BaseModel):
    doc:Optional[dict]

@app.post('/enrich/{index_name}')
async def enrich_document(index_name:str, document: IndexableDocument) -> dict:
    try:
        doc = document.doc
        enriched = pipelines.enrich(doc)
        idfield = config_json["id"]
        docid = doc[idfield]
        iq = skipchunk.index_connect
        saveDocument(docid,enriched,os.environ["DOCUMENTS_PATH"])
        res = enriched
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res

@app.post('/index/{index_name}')
async def index_document(index_name:str, document: IndexableDocument) -> dict:
    try:
        doc = document.doc
        enriched = pipelines.enrich(doc)
        idfield = config_json["id"]
        docid = doc[idfield]
        iq = skipchunk.index_connect(index_name)
        iq.indexDocument(enriched)
        saveDocument(docid,enriched,iq.engine.document_data)
        res = enriched
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res

@app.post('/reindex/{index_name}')
async def reindex_all_documents(index_name:str) -> dict:
    try:
        iq = skipchunk.index_connect(index_name)
        iq.indexGenerator(indexableDocuments(iq.engine.document_data))
        res = {"success":True}
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res

## ====================
## Search Proxy
## ====================

# Search the Solr core
@app.get('/solr/{index_name}')
async def solr_query(index_name: str, request: Request):
    #bypass fastAPI and just use starlette to get the querystring
    querystring = request.query_params
    params = []
    for t in querystring.items():
        key = t[0]
        val = t[1]
        if key in pipelines.queries.keys():
            print(key,val)
            val = pipelines.query(key,val)
            print(key,val)
        params.append(key+'='+urllib.parse.quote(str(val)))
    qs = '&'.join(params)
    uri = skipchunk.uri + index_name + '/select?' + qs
    res = await executor.passthrough(uri)
    return Response(content=res.text, media_type="application/json")

# Search the Elastic core
@app.post('/elastic/{index_name}')
async def elastic_query(index_name: str, request: Request) -> dict:
    #bypass fastAPI and just use starlette to get the body
    body = json.loads(await request.body())
    return await executor.passthrough(index_name,body)


## =====================
## Quepid/Splainer Proxy
## =====================


@app.get("/healthcheck")
async def health_check():
    """Health check"""
    return {"status": "OK"}

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
