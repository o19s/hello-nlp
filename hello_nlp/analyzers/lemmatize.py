from .interfaces import Doc_to_Doc_PipelineInterface
from spacy.tokens import Doc

_POS_LEMMA_ = {
	'ADJ'  , #adjective
	'ADV'  , #adverb
	'INTJ' , #interjection
	'NOUN' , #noun
	'PROPN', #proper noun
	'VERB' , #verb
}

class Lemmatizer(Doc_to_Doc_PipelineInterface):
	def analyze(self,doc: Doc):

		if not self.is_last_stage:
			return doc

		sentences = []
		for stream in doc.sents:
			lemmas = []
			for tok in stream:
				if (len(tok.text)>0) and (tok.is_alpha) and (len(tok.lemma_)>0) and (tok.pos_ in self.pos_lemma):
					ws = tok.text_with_ws.replace(tok.text,'')
					lemmas.append(tok.lemma_ + ws)

				else:
					lemmas.append(tok.text_with_ws)
			text = ''.join([t for t in lemmas if len(t)>0])

			sentences.append(text)

		return sentences

	def debug(self,text: str) -> str:
		if not self.is_last_stage:
			return "lemmatize = true"
		return text

	def __init__(self,metadata,pos_lemma=_POS_LEMMA_):
		self.name="lemmatize"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		self.pos_lemma = pos_lemma
		self.is_last_stage = False
		stages = self.pipeline["stages"]
		if "lemmatize" == stages[len(stages)-1]:
			self.is_last_stage = True
