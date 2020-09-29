import os
import json

def saveDocument(docid,doc,path):
    filename = path + '/' + docid + '.json'
    with open(filename,'w') as fd:
        json.dump(doc, fd)

def indexableDocuments(path):
    for f in os.listdir(path):
        filename = os.path.join(path, f) 
        if os.path.isfile(filename) and '.json' in filename:
            with open(filename,'r') as doc:
                yield json.load(doc)