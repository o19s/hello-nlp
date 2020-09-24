from .interfaces import Text_to_Doc_PipelineInterface
from spacy.tokens import Doc

import spacy

class Tokenizer(Text_to_Doc_PipelineInterface):

	def analyze(self,text:str)->Doc:
		return self.pipeline["nlp"](text)

	def __init__(self,metadata):
		self.name="Tokenizer"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		if "nlp" not in self.pipeline.keys():
			self.pipeline["nlp"] = spacy.load(self.pipeline["model"])
