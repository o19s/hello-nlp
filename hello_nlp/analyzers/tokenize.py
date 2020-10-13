from .interfaces import Text_to_Doc_PipelineInterface
from spacy.tokens import Doc
from spacy import displacy

class Tokenizer(Text_to_Doc_PipelineInterface):

	def tokenize(self,text:str)->Doc:
		docs = None
		for doc in self.pipeline["nlp"].pipe([text]):
			docs = doc
		return docs

	def analyze(self,text:str)->Doc:
		return self.tokenize(text)

	def debug(self,doc:Doc)->str:
		svgs = []
		for sent in doc.sents:
			svgs.append(displacy.render(sent, style="dep", jupyter=False))
		return svgs

	def __init__(self,metadata):
		self.name="tokenize"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		if "nlp" not in self.pipeline.keys():
			raise ValueError('Yo! Tokenizer needs Spacy to be added to the pipeline config first!')
