from .interfaces import Doc_to_Doc_PipelineInterface
from spacy.tokens import Doc

class Lemmatizer(Doc_to_Doc_PipelineInterface):
	def analyze(self,stream: Doc) -> Doc:
		return stream

	def debug(self,stream: Doc) -> str:
		return "lemmatize = True"


	def __init__(self,metadata):
		self.name="Lemmatizer"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		if "lemmatize" not in self.pipeline.keys():
			self.pipeline["lemmatize"] = True