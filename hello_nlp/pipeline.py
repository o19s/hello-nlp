import datetime
import spacy
from .analyzers import html_strip, tokenize, lemmatize, payload

from html import escape

pipelines = {
	"html_strip":html_strip.HTML_Strip,
	"tokenize":tokenize.Tokenizer,
	"lemmatize":lemmatize.Lemmatizer,
	"payload":payload.Payloader
}

def time():
	return datetime.datetime.now().timestamp() * 1000

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
		self.metadata = {"nlp":nlp}
		for stage in analyzers:
			if stage in pipelines.keys():
				self.stages.append(pipelines[stage](self.metadata))
		print(self.metadata)

class Field:
	def analyze(self,text: str, debug:bool=False) -> str:
		data,data_debug = self.analyzer.analyze(text,debug=debug)
		return data,data_debug 

	def __init__(self,field:dict,analyzer:Analyzer):
		self.source = field["source"]
		self.target = field["target"]
		self.analyzer = analyzer

class Pipelines:

	def analyze(self, analyzer:str, text:str, debug:bool=False) -> str:
		data,data_debug = self.analyzers[analyzer].analyze(text,debug=debug)
		return data,data_debug

	def enrich(self, document:dict, debug:bool=False) -> dict:
		for f in self.fields.keys():
			field = self.fields[f]
			data,data_debug = field.analyze(document[f],debug=debug)
			document[field.target] = data
		return document

	def add_analyzer(self, analyzer:dict):
		self.analyzers[analyzer["name"]] = Analyzer(analyzer["pipeline"],self.nlp)

	def add_field(self, field:dict):
		analyzer = self.analyzers[field["analyzer"]]
		self.fields[field["source"]] = Field(field,analyzer)

	def __init__(self,config):

		if "model" not in config.keys():
			raise ValueError("Yo! I need a model for spacy to load! Specify it as a model property in your config!")
		
		self.config = config

		self.nlp = spacy.load(self.config["model"])

		self.analyzers = {}
		for analyzer in config["analyzers"]:
			self.add_analyzer(analyzer)

		self.fields = {}
		for field in config["fields"]:
			self.add_field(field)
