![Hello-NLP Logo](/ui/img/logo.png)

Hello-NLP is a drop-in microservice to enhance your existing Solr or Elasticsearch index with the power of Python NLP.

In short, it exposes an enrichment service for a configurable analysis pipeline that aims to solve the naive normalization issues that happen during text analysis in Lucene search engines, and gives you the tools to craft business driven relevance without starting from scratch.

Hello-NLP is opinionated, but not imposing.  It doesn't try to assume what's relevant - but it does give you better tools and signals to use while you tune relevance.

Also, since the NLP community (mostly) uses Python, it brings Python extensibility to your content and query analysis that are otherwise unavailable in the Java-based Solr/Elastic stacks.  You can create an analyzer using Huggingface, SpaCy, Gensim, Scikit-learn, Pytorch, Tensorflow, or anything else you can imagine.  And, if you want to use a non-Python tool during analysis (like Duckling), it's easy to write a service call out using Python requests!

## Installation

Clone this repo!  Then check your configs:
- config.json
- solr.conf
- elasticsearch.conf
Install via either Docker or Manually

### Docker
Open the Dockerfile and change the run command to either run-solr.sh or run-elastic.sh, depending on your search engine.

Then build and run the container (will take a little while):

```bash
docker build -t hello_nlp .
docker run -p 5055:5055 hello_nlp
```

_ignore the nltk downloader and pip warnings - it's fine!_

### Manual

Install the dependencies

```bash
pip install -r requirements.txt
python -m spacy download 'en_core_web_lg'
python -m nltk.downloader wordnet
```

Then start either ```./run-solr.sh``` or ```./run-elastic.sh```

## Graph API

### GET /graph/{index_name}?query={query}

Gets the subject-predicate-object relationship graph for the subject ```{query}```

### GET /suggest/{index_name}?query={query}

Suggests noun phrases and verb phrases for autocomplete for the prefix ```{query}```

### GET /indexes/{index_name}

Gets the top 100 noun and verb phrases from your graph

## Content API

### GET /indexes

Gets the list of indexes on your Solr or Elasticsearch cluster

### GET /analyze/{analyzer}
_Coming soon!_

Analyzes the provided body text in the request with the given ```{analyzer}``` and returns the analyzed output

### POST /enrich/
_Coming soon!_

Analyzes a document and its fields according to the configured pipelines and returns the enriched document.  It also saves the enriched document on the service disc for easy reindexing.

### POST /index/
_Coming soon!_

Analyzes a document and its fields according to the configured pipelines, returns the enriched document, and sends the enriched document to your Solr or Elasticsearch cluster.  It also saves the enriched document on the service disc for easy reindexing.

### POST /reindex/
_Coming soon!_

Re-sends all your enriched documents from the Hello-NLP disc to your Solr or Elasticsearch cluster.  This does not re-enrich the documents!

### Motivations
Content enrichment in Hello-NLP looks to solve several problems inherent with trying to shoehorn this analysis into a Solr or Elasticsearch plugin.

1. Enrichment happens outside indexing!  A reindex doesn't require re-enrichment, which is often very slow.  You enrich ahead of time, save the document, and reindexing is a breeze.
2. You are not locked into the rigid Solr/Elastic plugin architecture, with annoying rebuilds and breaking API changes
3. You can be a Data Scientist or Python developer and avoid Java entirely.

### Why not Anserini?

Anserini is great, but still requires alot of legwork to get going, and usually requires maven and Java.  Hello-NLP is designed to work immediately as a microservice with minimal configuration, deployable via Docker straight to your stack.

## Query Enrichment API

Hello-NLP's pass-through query API evolved from https://github.com/amboss-mededu/quepid-es-proxy to be compatible with Quepid and Splainer out of the box, and also extended to support Solr.

### Motivations

Query enrichment and intent detection should be easier.  You can quickly write your own intent workflows using spaCy, Duckling, regex, or custom business rules in a Python script that you own and control.

### Elasticsearch Support

Just like a regular Elastic QueryDSL request, pass the query json as a body to ```POST /{index_name}/_search```

### Solr Support
_Coming soon!_
Just like a regular Solr request but pointed at Hello-NLP, pass your Solr querystrings into ```GET /{index_name}/solr/{request_handler}```

## Autocomplete

Hello-NLP exposes https://github.com/o19s/skipchunk graphs as an autocomplete service and graph exploration tool.  Browse noun phrases with ease and see which concepts appear together in sentences and documents.

## Analyzers

- html_strip (via bs4 and lxml)
- knowledge graph extraction (via skipchunk)
- coreference resolution (via neuralcoref) _(coming soon!)_
- tokenization (via spaCy)
- entity extraction (via spaCy) _(coming soon!)_
- lemmatization (via spaCy)
- semantic payloading (via spaCy)

### html_strip 

_TODO: Write this!_

### knowledge graph extraction 

_TODO: Write this!_

### tokenization 

_TODO: Write this!_

### lemmatization 

_TODO: Write this!_

### semantic payloading 

_TODO: Write this!_

## Pipeline

It's easy to configure and use an analysis pipeline!  If you've ever written one in Solr or Elasticsearch, you can pick it up in no time.

```json
{
    "analyzers": [
        {
            "name":"payloader",
            "pipeline":[
                "html_strip",
                "patternize",
                "tokenize",
                "lemmatize",
                "payload"
            ]
        }
    ],
    "fields": [
        {
            "source":"title",
            "target":"title_payloads",
            "analyzer":"payloader"
        },
        {
            "source":"content",
            "target":"content_payloads",
            "analyzer":"payloader"
        }
    ]
}
```