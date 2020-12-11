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

if os.environ["CUDA"] in ['true','cuda','True']:
    os.environ["CUDA"]="true"
    print("I will attempt to enable CUDA.")
else:
    os.environ["CUDA"]="false"
    print("CUDA is disabled. To enable it set CUDA=true in your *.conf file.")

with open('config.json','r') as fd:
    config_json = json.load(fd)

pipelines = Pipelines(config_json)

skipchunk = Connect(
    os.environ["ENGINE_USE_SSL"],
    os.environ["ENGINE_HOST"],
    os.environ["ENGINE_PORT"],
    os.environ["APP_NAME"],
    os.environ["ENGINE_NAME"],
    os.environ["DOCUMENTS_PATH"],
    config_json["model"])

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

@app.get('/')
async def index():
    """Redirects to the ui index.html page"""
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

@app.get('/suggest/{index_name}')
async def suggest(
    index_name: str, query: str
) -> dict:
    """Provides autocomplete suggestions, given a query prefix and graph index name"""
    gq = skipchunk.graph_connect(index_name)
    suggestions = gq.suggestConcepts(query)
    return {'suggestions':suggestions}

@app.get('/indexes')
async def indexes() -> dict:
    """Gets the list of search graph indexes"""
    indexes = skipchunk.gq.indexes()
    return {'indexes':indexes}

@app.get('/indexes/{index_name}')
async def index_summarize(index_name: str) -> dict:
    """Returns the top concepts and predicates for the given graph index"""
    gq = skipchunk.graph_connect(index_name)
    concepts,predicates = gq.summarize()
    return {'concepts':concepts,'predicates':predicates}

@app.get('/graph/{index_name}')
async def graph(index_name: str, subject: str) -> list:
    """Returnsthe graph walk for a subject term"""
    gq = skipchunk.graph_connect(index_name)
    objects = 5
    branches = 10
    tree = gq.graph(subject,objects=objects,branches=branches)
    return tree

@app.get('/analyzers')
async def analyzers() -> dict:
    """Returns a list of analyzers as provided in config.json"""
    try:
        data = list(pipelines.analyzers.keys())
        res = {'data':data}
    except ValueError as e:
        print(e)
        res = {'error':e}
    return res

@app.get('/analyze/{analyzer}')
async def analyze_text(analyzer: str, text: str, debug:bool=False) -> dict:
    """Analyzes the provided querystring text with the given analyzer"""
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
    """Analyzes the provided body text with the given analyzer"""
    try:
        data, data_debug = pipelines.analyze(analyzer,body.text,debug=debug)
        res = {"data":str(data),"debug":data_debug}
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res


class IndexableDocument(BaseModel):
    doc:Optional[dict]

class IndexableDocuments(BaseModel):
    docs:Optional[list]


@app.post('/enrich/{index_name}')
async def enrich_document(index_name:str, document: IndexableDocument) -> dict:
    """Enriches a document based on the field analysis as provided in config.json, saves the enriched document to disk, and returns the enriched document."""
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
    """Enriches a document based on the field analysis as provided in config.json, saves the enriched document to disk, and indexes the document in the search engine."""
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

@app.post('/bulk/{index_name}')
async def bulk_index_documents(index_name:str, document: IndexableDocuments) -> dict:
    """Bulk enriches the provided documents based on the field analysis as provided in config.json, saves the enriched documents to disk, and indexes the documents in the search engine.
       WARNING! Using the bulk operation will monopolize the service and block other calls.  It is recommended that bulk processing be done on a dedicated container.
    """
    try:
        iq = skipchunk.index_connect(index_name)
        idfield = config_json["id"]
        docs = document.docs
        enriched = []
        for doc in docs:
            docid = doc[idfield]
            analyzed = pipelines.enrich(doc)
            enriched.append(analyzed)
            saveDocument(docid,analyzed,iq.engine.document_data)
        iq.indexGenerator(enriched)
        res = {"success":True,"total":len(enriched)}
    except ValueError as e:
        print(e)
        res = {"error":e}
    return res

@app.post('/reindex/{index_name}')
async def reindex_all_documents(index_name:str) -> dict:
    """Sends all enriched documents on disk for indexing into the search engine.
       NOTE: this does NOT re-enrich the documents!
    """
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
    """Enriches a Solr query, and execute it against the search engine"""
    params = pipelines.solr_query(request.query_params)
    qs = '&'.join(params)    
    uri = skipchunk.uri + index_name + '/select?' + qs
    res = await executor.passthrough(uri)
    return Response(content=res.text, media_type="application/json")

# Enrich a Solr query
@app.get('/solr_enrich/{index_name}')
async def enrich_solr_query(index_name: str, request: Request) -> str:
    """Enriches a Solr query and returns it to the client without executing"""
    params = pipelines.solr_query(request.query_params)
    qs = '&'.join(params)    
    uri = skipchunk.uri + index_name + '/select?' + qs
    return uri


# Search the Elastic core
@app.post('/elastic/{index_name}')
async def elastic_query(index_name: str, request: Request) -> dict:
    """Enriches an Elastic QueryDSL request, and query the search engine"""
    body = json.loads(await request.body())
    enriched = pipelines.elastic_query(body)
    return await executor.passthrough(index_name,enriched)


# Enrich an Elastic query
@app.post('/elastic_enrich/{index_name}')
async def enrich_elastic_query(index_name: str, request: Request) -> dict:
    """Enriches an Elastic QueryDSL request and returns it to the client without executing"""
    body = json.loads(await request.body())
    return pipelines.elastic_query(body)


## =====================
## Quepid/Splainer Proxy
## =====================


@app.get("/healthcheck")
async def health_check():
    """Quepid health check call, just say 'yes' :)"""
    return {"status": "OK"}

@app.get("/explain/{index_name}")
async def explain_missing_documents(
    index_name: str,
    _source: str,
    q: str,
    size: int,
    username: str = Depends(basic_auth),
) -> dict:
    """Quepid explain missing documents query for Solr"""
    result = await executor.passthrough(
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
    """Quepid explain missing documents query for Elasticsearch"""
    return await executor.explain(index_name, doc_id, query)
