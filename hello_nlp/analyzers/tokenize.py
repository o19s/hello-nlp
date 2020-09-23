import spacy

class Tokenizer:

	def analyze(self,stream):
		return self.pipeline["nlp"](text)

	def __init__(self,metadata):
		self.name="Tokenizer"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		if "nlp" not in self.pipeline.keys():
			self.pipeline["nlp"] = spacy.load(self.pipeline["model"])
