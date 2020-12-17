from skipchunk.skipchunk import Skipchunk, textFromFields
from skipchunk.graphquery import GraphQuery
from skipchunk.indexquery import IndexQuery
from skipchunk.enrichquery import EnrichQuery

def tuplize(data,fields=[],strip_html=True):
    tuples = []
    for post in data:
        text = textFromFields(post,fields,strip_html=strip_html)
        tuples.append((text,post))
    return tuples

class Connect:

    def __init__(self,use_ssl,host,port,index,engine_name,path,model,settings):

        uri = ""

        if use_ssl in ["True","true",True,1,"1"]:
            uri += 'https://'
        else:
            uri += 'http://'

        uri += host + ":" + str(port) + "/"

        if engine_name in ["solr"]:
            uri += "solr/"

        self.config = {
            "host":uri,
            "name":index,
            "engine_name":engine_name,
            "path":path,
            "model":model
        }

        self.uri = uri

        self.fields = settings.pop("fields")

        self.sc = Skipchunk(self.config,spacy_model=model,**settings)
        print("But no need to worry, Hello-NLP is saving your stuff.")

        self.eq = EnrichQuery(model=model)
        self.iq = IndexQuery(self.config,enrich_query=self.eq)
        self.gq = GraphQuery(self.config)

        self.graph_connections = {}
        self.index_connections = {}

    def graph_connect(self,name):
        if name not in self.graph_connections.keys():
            graph_config = self.config.copy()
            graph_config["name"] = name
            self.graph_connections[name] = GraphQuery(graph_config)
        return self.graph_connections[name]

    def index_connect(self,name):
        if name not in self.index_connections.keys():
            index_config = self.config.copy()
            index_config["name"] = name
            self.index_connections[name] = IndexQuery(index_config,enrich_query=self.eq)
        return self.index_connections[name]

    def extract_one(self,name,doc):
        tuples = tuplize([doc],fields=self.fields)
        self.sc.enrich(tuples)
        gq = self.graph_connect(name)
        gq.index(self.sc)

    def extract_batch(self,name,docs):
        tuples = tuplize(docs,fields=self.fields)
        self.sc.enrich(tuples)
        gq = self.graph_connect(name)
        gq.index(self.sc)
