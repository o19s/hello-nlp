import spacy
from .analyzers import html_strip, tokenize, lemmatize, payload

pipelines = {
	"html_strip":html_strip.HTML_Strip,
	"tokenize":tokenize.Tokenizer,
	"lemmatize":lemmatize.Lemmatizer,
	"payloader":payload.Payloader
}

class Analyzer:
	def analyze(self,text: str) -> str:
		data = text
		for stage in self.stages:
			data = stage.analyze(data)
		text = data
		return text

	def __init__(self,analyzers,nlp):
		self.stages = []
		self.metadata = {"nlp":nlp}
		for stage in analyzers:
			if stage in pipelines.keys():
				self.stages.append(pipelines[stage](self.metadata))
		print(self.metadata)

class Field:
	def analyze(self,text: str) -> str:
		return analyzer.analyze(text)

	def __init__(self,field:dict,analyzer:Analyzer):
		self.source = field["source"]
		self.target = field["target"]
		self.analyzer = analyzer

class Pipelines:

	def enrich(self,document:dict) -> dict:
		for f in self.fields.keys():
			field = self.fields[f]			
			document[field.target] = field.analyze(document[f])

	def add_analyzer(self,analyzer):
		self.analyzers[analyzer["name"]] = Analyzer(analyzer["pipeline"],self.nlp)

	def add_field(self,field):
		analyzer = self.analyzers[field["analyzer"]]
		self.fields[field["source"]] = Field(field,analyzer)

	def __init__(self,config):

		if "model" not in config.keys():
			raise ValueError("Yo! I need a model for spacy to load! Specify it as a model property in your config!")
		
		self.config = config

		self.nlp = spacy.load(self.config["model"])

		self.analyzers = {}
		for analyzer in config["analyzers"]:
			self.add(analyzer)

		self.fields = {}
		for field in config["fields"]:
			self.add(field)