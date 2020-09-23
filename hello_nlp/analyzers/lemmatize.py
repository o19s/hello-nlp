from spacy.tokens import Doc

class Lemmatizer:
	def analyze(self,stream: Doc) -> Doc:
		return stream

	def __init__(self,metadata):
		self.name="Lemmatizer"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		if "lemmatize" not in self.pipeline.keys():
			self.pipeline["lemmatize"] = True