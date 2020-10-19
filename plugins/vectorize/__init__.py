import base64
import numpy as np
from spacy.tokens import Doc

def quantize(data,scale):
    data = data.astype(np.float32) / scale # normalize the data
    norm = 255 * data # Now scale by 255
    norm = norm.astype(np.int8) # Cast to signed integer
    b64e = base64.b64encode(norm) # Encode it
    return b64e

def extract_vectors(doc:Doc) -> list:
    vecs = []
    scale = -999999.00
    for span in doc.sents:
        if span.has_vector:
            v = span.vector
            m = max(v)
            i = abs(min(v))
            if m>scale:
                scale = m
            if i>scale:
                scale = i
            vecs.append(v)
    quantized = [quantize(v,scale) for v in vecs]
    return quantized

## --------------------------------------

## The following are required:
##   - This file must be named __init__.py
##   - The folder name must match self.name
##   - The class name must be 'Plugin'
##   - The Plugin class must implement the 'analyze' method
##   - The Plugin class must implement the 'debug' method

##   - Please Enjoy and happy searching!!

class Plugin():

    def analyze(self,doc:Doc)->list:
        vectors = extract_vectors(doc)
        return vectors

    def debug(self,vectors:list)->list:
        return vectors
        
    def __init__(self,metadata):
        self.name="vectorize"
        self.pipeline = metadata
        self.pipeline[self.name] = True
        self.index = None
