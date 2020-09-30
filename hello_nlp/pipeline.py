import datetime
import spacy

from html import escape

from .analyzers import html_strip, tokenize, lemmatize, payload
from .plugins import load_plugin, get_plugins

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
		text = data
		data_debug.append({"name":"(end)","time":total_time,"debug":text})
		return text,data_debug

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

	def query(self,key:str,data:str, debug:bool=False) -> dict:
		if key in self.queries.keys():
			enrichers = self.queries[key]
			for enricher in enrichers:
				data,data_debug = enricher.analyze(data,debug=debug)
		if isinstance(data,list):
			data = ' '.join(data)
		return data

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
		self.fields[field["source"]].append(Field(field,analyzer))

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
		for field in config["fields"]:
			self.add_field(field)

		self.queries = {}
		for query in config["query"]:
			self.add_query(query)
