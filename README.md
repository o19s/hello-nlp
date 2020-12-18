![Hello-NLP Logo](/ui/img/logo.png)

Hello-NLP is a drop-in microservice to enhance Solr or Elasticsearch with the power of Python NLP.  It is written to be a practical addition to your search relevance stack with minimal learning curve to get you running quickly and efficiently.

In short, it exposes an enrichment service for a configurable analysis pipeline that aims to solve the naive normalization issues that happen during text analysis in Lucene search engines, and gives you the tools to craft business driven relevance without starting from scratch.

Hello-NLP is opinionated, but not imposing.  It doesn't try to assume what's relevant - but it does give you better tools and signals to use while you tune relevance.  If you're used to crafting analyzers in Elastic or fieldTypes in Solr, then you'll feel comfortable with Hello-NLP.

Also, since the NLP community (mostly) uses Python, it brings Python extensibility to your content and query analysis that are otherwise unavailable in the Java-based Solr/Elastic stacks.  You can create an analyzer using Huggingface, SpaCy, Gensim, Scikit-learn, Pytorch, Tensorflow, or anything else you can imagine.  And, if you want to use a non-Python tool during analysis (like Duckling), it's easy to write a service call out using Python requests!

## Installation

Clone this repo!  Then Install via either Docker or Manually


### Docker for Solr

Open your configuration file ```docker-solr.conf```, and configure your connectivity to your running Solr endpoint.

Then build and run the container (will take a little while the first time, but starts up more quickly afterwards):

```bash
./docker-solr.sh
```

You'll know when it finished running when you see the following:

```bash
"hello-nlp-solr_1  | INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:5050 (Press CTRL+C to quit)"
```

Now run the example ```example/index-one.sh``` script files to index a document!

You can then access the Admin UI and API docs at http://localhost:5050 ...check that out and browse around a little while.

Now, open the ```pipeline-solr.json``` file.  This is your pipeline, we will explain how this all works next.


### Docker for Elasticsearch

Open your configuration file ```docker-elasticsearch.conf```, and configure to connectivity to your running __Elasticsearch__ cluster.

Then build and run the container (will take a little while the first time, but starts up more quickly afterwards):

```bash
./docker-elasticsearch.sh
```

You'll know when it finished running when you see the following:

```bash
"hello-nlp-elasticsearch_1  | INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:5055 (Press CTRL+C to quit)"
```

Now run the example ```example/index-one.sh``` script files to index a document!

You can then access the Admin UI and API docs at http://localhost:5055 ...check that out and browse around a little while.

Now, open the ```pipeline-elasticsearch.json``` file.  This is your pipeline, we will explain how this all works next.

### Manual Installation

Install the dependencies (make sure you download the same model that you use in the pipeline configuration below!)

```bash
pip install -r requirements.txt
python -m spacy download 'en_core_web_lg'
python -m nltk.downloader wordnet
```

Check your configs
- config.json
- solr.conf (if you're using Solr)
- elasticsearch.conf (if you're using Elasticsearch)

Then start either ```./run-solr.sh``` or ```./run-elasticsearch.sh```

Now run the example ```example/solr-index-one.sh``` or ```example/elasticsearch-index-one.sh``` script files to index a document!

You can then access the Admin UI and API docs at http://localhost:5055 ...check that out and browse around a little while.

Now, open the ```pipeline-solr.json``` or ```pipeline-elasticsearch.json``` file.  This is your pipeline, we will explain how this all works next.


## Your New Enrichment Pipeline

It's easy to configure and use an analysis pipeline!  If you've ever written one in Solr or Elasticsearch, you can pick it up in no time.

We're going to show you a whole pipeline, which must always located in [conf.json](conf.json), and then walk you through the parts.

```json
{
    "id": "id",
    "model": "en_core_web_lg",
    "plugin_path": "./plugins",
    "analyzers": [
        {
            "name":"payloader",
            "pipeline":[
                "html_strip",
                "tokenize",
                "payload"
            ]
        },
        {
            "name":"entitizer",
            "pipeline":[
                "html_strip",
                "tokenize",
                "entitize"
            ]
        },
        {
            "name":"lemmatizer",
            "pipeline":[
                "html_strip",
                "tokenize",
                "lemmatize"
            ]
        },
        {
            "name":"prepositionizer",
            "pipeline":[
                "html_strip",
                "tokenize",
                "prepositionize"
            ]
        },
        {
            "name":"vectorizer",
            "pipeline":[
                "html_strip",
                "tokenize",
                "vectorize"
            ]
        }
    ],
    "fields": [
        {
            "source":"title",
            "target":"title_txt",
            "analyzer":"lemmatizer"
        },
        {
            "source":"title",
            "target":"title_payloads",
            "analyzer":"payloader"
        },
        {
            "source":"content",
            "target":"content_payloads",
            "analyzer":"payloader"
        },
        {
            "source":"content",
            "target":"people_ss",
            "analyzer":"entitizer"
        },
        {
            "source":"title",
            "target":"title_vector",
            "analyzer":"vectorizer"
        }
    ],
    "skipchunk": {
        "fields":["title","content"],
        "minconceptlength":1,
        "maxconceptlength":3,
        "minpredicatelength":1,
        "maxpredicatelength":3,
        "minlabels":1,
        "cache_documents":false,
        "cache_pickle":false
    }
}
```

### How the Pipeline works:


__Your CMS__ ```--(raw-documents)-->``` __Hello-NLP__ ```--(enriched-documents)-->``` __Solr/Elasticsearch__


You send content to Hello-NLP the same way you send it to your search engine.  You provide documents, and those documents contain fields.  Those fields are parsed and changed in an analyzer, based on the type of the field, and then sent into the search engine.  You can also copy fields to a new field with its own type, so you can analyze the same field in different ways.

Let's use a simple example: *Lemmatization*.  You have a title field that you want to Lemmatize (normalize to the root form of the words) so that words like 'cars' will be normalized as 'car', and searching for either will match the title.

For example, a title may contain entities that you want to extract, so you can copy the title to a new field *"title_ss"* (where ```_ss``` will be indexed as a dynamic multivalued string field).  Then you specify that the field has the analyzer *"entitize"*.

First, we need an analyzer:

```json
{    
    ...
    "analyzers": [
        ...,
        {
            "name":"lemmatizer",
            "pipeline":[
                "html_strip",
                "tokenize",
                "lemmatize"
            ]
        },...
    ]
    ...
}
```

With the analyzer configured, now you can use it when processing fields.  Following the same lemmatization example:

```json
{    
    ...
    "fields": [
        ...,
        {
            "source":"title",
            "target":"title_txt",
            "analyzer":"lemmatizer"
        },...
    ]
    ...
}
```

With the above entries in your pipeline, when indexing a document, the title field will be copied to a new field title_txt, and that copy will be processed by the lemmatizer analyzer.


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

Analyzes the provided body text in the request with the given ```{analyzer}``` and returns the analyzed output

### POST /enrich/

Analyzes a document and its fields according to the configured pipelines and returns the enriched document.  It also saves the enriched document on the service disc for easy reindexing.

### POST /index/

Analyzes a document and its fields according to the configured pipelines, returns the enriched document, and sends the enriched document to your Solr or Elasticsearch cluster.  It also saves the enriched document on the service disc for easy reindexing.

### POST /reindex/

Re-sends all your enriched documents from the Hello-NLP disc to your Solr or Elasticsearch cluster.  This does not re-enrich the documents!

## Query Enrichment API

Hello-NLP's Query API exposes python NLP enrichment and query rewriting to your existing query parser

### Motivations

Query enrichment and intent detection should be easier.  You can quickly write your own intent workflows using spaCy, Duckling, regex, or custom business rules in a Python script that you own and control, and then dynamically reference them at querytime.

### Solr Support

Just like a regular Solr request but pointed at Hello-NLP, pass your Solr querystrings into ```GET /solr/{index_name}?q=...```

Here's an example of removing negative prepositions using a simple querywriter, inlined as a Solr subquery:

```
q=shirt without stripes
&fq={!hello_nlp f=-style:$v v=$q analyzer=prepositionizer}
```

Will expand to:

```
q=shirt
&fq=-style:stripe
```

### Elasticsearch Support

Just like a regular Elastic QueryDSL request, pass the query json as a body to ```POST /elastic/{index_name}```

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

Removes HTML and XML tags from text, using well supported parsers like lxml or beautifulsoup4

### coreference resolution 

_(coming soon!)_

Uses neuralcoref for in-place rewriting of pronouns with their nouns.

### knowledge graph extraction 

Uses Skipchunk to extract a vocabulary and latent knowledge graph to be used as a read-to-go autocomplete

### patternization 

_(coming soon!)_

Uses Duckling to identify loosely structured value entities and replaces them with canonical forms

### tokenization 

Uses SpaCy to tokenize and tag text that can be used later in the analysis chain

### entity extraction

Copies text-embedded entities of specific classes to other fields, for faceting and filtering.  Currently offered as an example plugin.

### vectorization

Uses https://sbert.net/ to get transformer embeddings and copy them into a vector field for nearest-neighbor search, fine-tuning, and other tasks.

### lemmatization 

Lemmatizes Nouns and Verbs to their root form, as a more precise alternative to stemming

### semantic payloading 

Attaches weights to parts-of-speech and entities, that will be expressed as delimited payloads for Lucene.


## Making Your Own Analyzers

_TL;DR;_ *Go to the plugins folder, copy one of the plugin folders, give it a good name, and tweak its __init__.py file!  Then reference it in your pipeline analyzers, fields, and queries*

While Hello-NLP offers core analyzers out of the box, there are lots of things you might want to do to meet your own search use cases.  Plugins are the same thing as analyzers, but you write and maintain them yourself.

It's easy to make a plugin, but there are some important conventions you must follow.

* Plugins must be placed in ```plugin_path``` that you reference in your ```config.json``` file.
* Each plugin consists of a folder bearing the same name as the plugin.  For example, a plugin named "peoplizer" must be in the path ```plugin_path/peoplizer/```
* The source of the plugin must be in a file named ```__init__.py``` and be placed in the root of the plugin's folder.  Following the same example above: ```plugin_path/peoplizer/__init__.py```

In the code of the plugin's ```__init__.py``` file, the following are required:

* There must be a class and the name must be 'Plugin'
* The parent folder name must match self.name of the Plugin class, which is set during object instantiation.
* The Plugin class must implement the 'analyze' method
* The Plugin class must implement the 'debug' method

Use duck typing to chain plugins and analyzers together in your pipelines!

* Each plugin or analyzer accepts one variable and outputs returns variable
* The input object MUST match the type (or be implicitly castable) of the output of the plugin/analyzer in the previous stage
* The output object MUST be consumable as input by the following plugin/analyzer stage

There are a couple example plugins already to get you started, in the ```./plugins``` folder of this repo.  Feel free to copy and modify them to suit your needs!