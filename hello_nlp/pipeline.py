import spacy
from .analyzers import html_strip, tokenize, lemmatize, payload

pipelines = {
	"html_strip":html_strip.HTML_Strip,
	"tokenize":tokenize.Tokenizer,
	"lemmatize":lemmatize.Lemmatizer,
	"payloader":payload.Payloader
}

class Pipeline:
	def analyze(self,text: str) -> str:
		data = text
		for stage in self.stages:
			data = stage.analyze(data)
		text = data
		return text

	def __init__(self,analyzers):
		self.metadata = {"model":"en_core_web_lg"}
		self.stages = []
		for stage in analyzers:
			if stage in pipelines.keys():
				self.stages.append(pipelines[stage](self.metadata))
		print(self.metadata)

class Pipelines:
	def add(self,field):
		self.fields[field["field"]] = Pipeline(field["pipeline"])

	def __init__(self,config):
		self.fields = {}
		for field in config:
			self.add(field)

"""
[
	{
		"field":"title",
		"pipeline":[
			"html_strip",
			"patternize",
			"tokenize",
			"entitize",
			"lemmatize",
			"payload"
		]
	},
	{
		"field":"content",
		"pipeline":[
			"html_strip",
			"patternize",
			"tokenize",
			"entitize",
			"lemmatize",
			"payload"
		]
	}
]
"""