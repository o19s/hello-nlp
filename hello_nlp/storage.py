import os
import json

def saveDocument(docid,doc,path):
    if not os.path.isdir(path):
        os.makedirs(path)

    filename = path + '/' + docid + '.json'
    with open(filename,'w',encoding='utf-8') as fd:
        json.dump(doc, fd)

def indexableDocuments(path):
    if not os.path.isdir(path):
        os.makedirs(path)

    for f in os.listdir(path):
        filename = os.path.join(path, f) 
        if os.path.isfile(filename) and '.json' in filename:
            with open(filename,'r') as doc:
                yield json.load(doc)