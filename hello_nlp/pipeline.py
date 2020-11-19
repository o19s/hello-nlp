import datetime
import spacy
import re
import urllib

import json

from html import escape

from .analyzers import html_strip, tokenize, lemmatize, payload
from .plugins import load_plugin, get_plugins

from .query import queryparser

#from .elastic import parser as elastic_parser
#from .solr import parser as solr_parser

#------------------------------------------

def time():
    return datetime.datetime.now().timestamp() * 1000

#------------------------------------------

pipelines = {
    "html_strip":html_strip.HTML_Strip,
    "tokenize":tokenize.Tokenizer,
    "lemmatize":lemmatize.Lemmatizer,
    "payload":payload.Payloader
}

def add_to_pipelines(plugin:dict):
    pipelines[plugin["name"]] = load_plugin(plugin).Plugin

#------------------------------------------

class Analyzer:
    def analyze(self, text: str, debug:bool=False) -> str:
        data = text
        data_debug = []
        total_time = 0
        if debug:
            data_debug.append({"name":"(start)","time":0,"debug":escape(text)})
        for stage in self.stages:
            if debug:
                startwatch = time()
            data = stage.analyze(data)
            if debug:
                stopwatch = time() - startwatch
                total_time += stopwatch
                data_debug.append({"name":stage.name,"time":stopwatch,"debug":stage.debug(data)})
        if debug:
            data_debug.append({"name":"(end)","time":total_time,"debug":data})
        return data,data_debug

    def __init__(self,analyzers,nlp):
        self.stages = []
        self.metadata = {"nlp":nlp,"stages":[]}
        for stage in analyzers:
            if stage in pipelines.keys():
                self.metadata["stages"].append(stage)
                self.stages.append(pipelines[stage](self.metadata))
        print(self.metadata)

#------------------------------------------

class Field:
    def analyze(self,text: str, debug:bool=False) -> str:
        data,data_debug = self.analyzer.analyze(text,debug=debug)
        return data,data_debug 

    def __init__(self,field:dict,analyzer:Analyzer):
        self.source = field["source"]
        self.target = field["target"]
        self.analyzer = analyzer

#------------------------------------------

class Query:
    def analyze(self,text: str, debug:bool=False) -> str:
        data,data_debug = self.analyzer.analyze(text,debug=debug)
        return data,data_debug 

    def __init__(self,query:dict,analyzer:Analyzer):
        self.source = query["source"]
        self.target = query["target"]
        self.analyzer = analyzer

#------------------------------------------

class Pipelines:    

    def analyze(self, analyzer:str, text:str, debug:bool=False) -> str:
        data,data_debug = self.analyzers[analyzer].analyze(text,debug=debug)
        return data,data_debug

    def enrich(self, document:dict, debug:bool=False) -> dict:
        for f in self.fields.keys():
            fields = self.fields[f]
            for field in fields:
                data,data_debug = field.analyze(document[f],debug=debug)
                document[field.target] = data
        return document

    def query(self, key:str, data:str, debug:bool=False) -> dict:
        if key in self.queries.keys():
            enrichers = self.queries[key]
            for enricher in enrichers:
                data,data_debug = enricher.analyze(data,debug=debug)
        if isinstance(data,list):
            data = ' '.join(data)
        return data

    def solr_query(self,querystring):
        params = []
        q_param = ""
        for t in querystring.items():
            key = t[0]
            val = t[1]
            if key in self.queries.keys():
                val = self.query(key,val)
                if key == "q":
                    q_param = val
                else:
                    params.append(key+'='+urllib.parse.quote(str(val)))

            else:
                resolved = val

                #Detects and parses a {!hello_nlp ...} subquery
                template,analyzer,text = queryparser(q_param,val)
                print(template,analyzer,text)

                #Expands the subquery to its resolved text
                if (analyzer in self.analyzers.keys()) and len(text):
                    analyzer = self.analyzers[analyzer]
                    resolved,resolved_debug = analyzer.analyze(text,debug=False)
                    
                    if isinstance(resolved,dict):
                        v = None
                        if 'v' in resolved.keys() and (len(resolved["v"])) :
                            v = ' '.join(resolved["v"])
                            val = template.replace('$v',str(v))
                            params.append(key+'='+urllib.parse.quote(str(val)))
                        if 'q_param' in resolved.keys() and (len(resolved["q_param"])) :
                            q_param = resolved["q_param"]

                    else:
                        if isinstance(resolved,list):
                            resolved = ' '.join(resolved)
                        resolved = str(resolved)

                        if len(resolved):
                            val = template.replace('$v',str(resolved))
                            params.append(key+'='+urllib.parse.quote(str(val)))
                            print(key,val)
                else:
                    params.append(key+'='+urllib.parse.quote(str(val)))

        params.append('q='+urllib.parse.quote(q_param))

        return params

    def elastic_query(self,obj,enrich=None):

        keywords = {"query","match","match_phrase","match_all","should","must","should_not","must_not","filter","bool","term","terms","script_score","params","script","rescore","rescore_query","function_score"}

        if isinstance(obj,dict):

            for key in obj.keys():
                #print(key)

                if key == "!hello_nlp":
                    name = obj[key]["name"]
                    value = obj[key]["value"]
                    analyzer = obj[key]["analyzer"]
                    analyzed = self.analyzers[analyzer].analyze(value,debug=False)
                    return {name:analyzed[0]}

                elif (key in self.queryfields):
                    #print('fields')
                    if isinstance(obj[key],str):
                        #print('ANALYZE A')
                        data,_ = self.query_analyzer.analyze(obj[key],debug=False)
                        obj[key] = str(data)
                    else:
                        #print('RECURSE A')
                        obj[key] = self.elastic_query(obj[key],enrich=key)

                elif key in keywords:
                    #print('KEYWORD')
                    if isinstance(obj[key],str):
                        #print(obj[key])
                        if isinstance(enrich,str):
                            #print('ANALYZE B')
                            data,_ = self.query_analyzer.analyze(obj[key],debug=False)
                            obj[key] = str(data)
                    else:
                        #print('RECURSE B')
                        obj[key] = self.elastic_query(obj[key],enrich=enrich)

        elif isinstance(obj,list):
            for i in range(len(obj)-1):
                if isinstance(obj[i],str):
                    #print(i,obj[i])
                    if (enrich):
                        #print('ANALZE C')
                        data,_ = self.query_analyzer.analyze(obj[i],debug=False)
                        obj[i] = str(data)
                else:
                    #print('RECURSE C')
                    obj[i] = self.elastic_query(obj[i],enrich=enrich)

        #print('DONE')
        #print(json.dumps(obj,indent=2))
        return obj

    """
    def query(self,params:dict) -> dict:
        for f in self.queries.keys():
            queries = self.queries[f]
            for query in queries:
                data,data_debug = query.analyze(params[f],debug=debug)
                params[query.target] = data
        return params
    """

    def add_analyzer(self, analyzer:dict):
        self.analyzers[analyzer["name"]] = Analyzer(analyzer["pipeline"],self.nlp)

    def add_field(self, field:dict):
        analyzer = self.analyzers[field["analyzer"]]
        if field["source"] not in self.fields.keys():
            self.fields[field["source"]] = []   
        newfield = Field(field,analyzer)
        self.fields[field["source"]].append(newfield)
        self.queryfields.add(newfield.source)
        self.queryfields.add(newfield.target)

    def add_query(self, query:dict):
        analyzer = self.analyzers[query["analyzer"]]
        if query["source"] not in self.queries.keys():
            self.queries[query["source"]] = []  
        self.queries[query["source"]].append(Query(query,analyzer))

    def __init__(self,config):

        if "model" not in config.keys():
            raise ValueError("Yo! I need a model for spacy to load! Specify it as a model property in your config!")

        self.config = config

        self.nlp = spacy.load(self.config["model"])

        self.plugins = {}
        if "plugin_path" in config.keys():
            for plugin in get_plugins(config["plugin_path"]):
                add_to_pipelines(plugin)

        self.analyzers = {}
        for analyzer in config["analyzers"]:
            self.add_analyzer(analyzer)

        self.fields = {}
        self.queryfields = set()
        for field in config["fields"]:
            self.add_field(field)

        self.queries = {}
        for query in config["query"]:
            self.add_query(query)


        if len(config["query"])>0:
            self.query_analyzer = self.analyzers[config["query"][0]["analyzer"]]
        else:
            self.query_analyzer = self.analyzers["lemmatizer"]

