import os
import numpy as np
from spacy.tokens import Doc
from sentence_transformers import SentenceTransformer

## --------------------------------------

## The following are required:
##   - This file must be named __init__.py
##   - The folder name must match self.name
##   - The class name must be 'Plugin'
##   - The Plugin class must implement the 'analyze' method
##   - The Plugin class must implement the 'debug' method

##   - Please Enjoy and happy searching!!

class Plugin():

    def analyze(self,doc:Doc,context:dict=None)->list:
        #This example only analyzes the first sentence of the document
        #Dense Vector fields in Elastic/Solr are not multivalued
        #When you use this in real life, distill all sentences down to one vector
        sentence = [span.text for span in doc.sents][0]
        embeddings = self.model.encode([sentence])
        vector = [embedding.tolist() for embedding in embeddings][0]
        return vector

    def debug(self,vector:list,context:dict=None)->list:
        return vector
        
    def __init__(self,metadata):
        self.name="vectorize"
        self.pipeline = metadata
        self.pipeline[self.name] = True
        self.index = None

        self.cuda=os.environ["CUDA"]
        self.device='cpu'
        if self.cuda=='true':
            self.device='cuda'

        #To use CUDA on your system/container, set CUDA=true in /hello-nlp/config.json
        self.model = SentenceTransformer('https://sbert.net/models/distilbert-base-nli-stsb-mean-tokens.zip',device=self.device)