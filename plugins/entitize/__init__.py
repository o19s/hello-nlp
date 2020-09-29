from spacy.tokens import Doc
from spacy import displacy,util

## --------------------------------------
## Adopted from https://spacy.io/usage/examples#entity-relations

def filter_spans(spans):
    # Filter a sequence of spans so they don't contain overlaps
    # For spaCy 2.1.4+: this function is available as spacy.util.filter_spans()
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result

def extract_people(doc):
    # Merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = util.filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)

    #Get the folks
    people = [str(person) for person in filter(lambda w: w.ent_type_ == "PERSON", doc)]
    return people

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
        sentences = []
        people = extract_people(doc)
        return people

    def debug(self,doc:Doc)->list:
        #return list(doc)
        return []
        
    def __init__(self,metadata):
        self.name="entitize"
        self.pipeline = metadata
        self.pipeline[self.name] = True