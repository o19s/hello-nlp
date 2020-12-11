# -*- coding: utf-8 -*-

from .interfaces import Doc_to_Text_PipelineInterface
from spacy.tokens import Doc


"""
Payloads are assigned to Open Class Words ONLY!

https://universaldependencies.org/docs/u/pos/

Open class words 	Closed class words 	Other
----------------	------------------	-----
ADJ 				ADP 				PUNCT
ADV 				AUX 				SYM
INTJ 				CONJ 				X
NOUN 				DET 	 
PROPN 				NUM 	 
VERB 				PART 	 
  					PRON 	 
  					SCONJ 	 
"""

_POS_SCORES_ = {
	'ADJ'  :  1.5, 	#adjective
	'ADV'  :  1.5, 	#adverb
	'INTJ' :  1.0, 	#interjection
	'NOUN' :  2.0, 	#noun
	'PROPN':  2.0, 	#proper noun
	'VERB' :  2.0   #verb
}

"""
Part of Speech payloads are cool, but the real juice is from dependencies!
Specifically: subjects, objects, and roots.

Intuition: the "aboutness" of sentences is more important than just the concepts mentioned.
"""

_DEP_SCORES_ = {
	'nsubjpass': 2.0,
	'nsubj'    : 2.0,
	'dobj'     : 2.0,
	'pobj'     : 1.5,
	'root'     : 2.0
}


class Payloader(Doc_to_Text_PipelineInterface):

	def analyze(self, doc:Doc, context:dict=None) -> str:
		
		sentences = []

		for stream in doc.sents:

			payloads = []

			for tok in stream:
				score = None

				if (len(tok.text)>0) and (self.delimiter not in tok.text):

					if (tok.is_alpha) and (len(tok.lemma_)>0) and (tok.pos_ in self.pos_scores):
						score = self.pos_scores[tok.pos_]

						if tok.dep_ in self.dep_scores:
							score += self.dep_scores[tok.dep_]

						value = str(score) # + 'f'

						payloads.append(tok.lemma_ + self.delimiter + value + ' ')

					else:
						payloads.append(tok.text_with_ws)

				else:
					#We need to remove any other delimiter chars in the text
					#Otherwise it will be picked up by the PayloadDelimiterFilter
					payloads.append(tok.text_with_ws.replace(self.delimiter,''))


			text = ''.join([t for t in payloads if len(t)>0])

			sentences.append(text)

		return sentences

	def debug(self,text:str,context:dict=None) -> str:
		return text

	def __init__(self,metadata,delimiter='|',pos_scores=_POS_SCORES_,dep_scores=_DEP_SCORES_):
		self.name="payload"
		self.pipeline = metadata
		self.pipeline[self.name] = True

		self.delimiter = delimiter
		self.dep_scores = dep_scores
		self.pos_scores = pos_scores

