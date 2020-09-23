from skipchunk.graphquery import GraphQuery
from skipchunk.indexquery import IndexQuery
from skipchunk.enrichquery import EnrichQuery

class Connect:

    def __init__(self,use_ssl,host,port,index,engine_name,path):

        uri = ""

        if use_ssl in ["True","true",1,"1",True]:
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
            "path":path

        }

        self.uri = uri

        self.eq = EnrichQuery(model='en_core_web_lg')
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