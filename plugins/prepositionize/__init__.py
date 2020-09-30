from spacy.tokens import Doc
from spacy import displacy,util

## --------------------------------------

def rewrite(text,vals):
    for v in vals:
        text = text.replace(v,'')
    return text.strip()

def prepose(doc):
    preps = [tok.text for tok in doc if tok.dep_=='prep']
    pobjs = [tok.text for tok in doc if tok.dep_=='pobj']
    return preps,pobjs

## The following are required:
##   - This file must be named __init__.py
##   - The folder name must match self.name
##   - The class name must be 'Plugin'
##   - The Plugin class must implement the 'analyze' method
##   - The Plugin class must implement the 'debug' method

##   - Please Enjoy and happy searching!!

class Plugin():

    def analyze(self,doc:Doc)->dict:
        preps,pobjs = prepose(doc)
        text = doc.text
        data = {"q":text}
        if 'without' in preps:
            data["q_param"] = rewrite(text,preps+pobjs)
            data["v"] = pobjs
        return data

    def debug(self,doc:Doc)->dict:
        preps,pobjs = prepose(doc)
        text = doc.text
        data = {"q":text}
        if 'without' in preps:
            data["q_param"] = rewrite(text,preps+pobjs)
            data["v"] = pobjs
        return data
        
    def __init__(self,metadata):
        self.name="prepositionize"
        self.pipeline = metadata
        self.pipeline[self.name] = True
        self.rewriter = True