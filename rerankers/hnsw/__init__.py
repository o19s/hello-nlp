import nmslib
import base64
import numpy as np

# query for the nearest neighbours of the first datapoint
#ids, distances = index.knnQuery(data[0], k=10)

# get all nearest neighbours for all the datapoint
# using a pool of 4 threads to compute
#neighbours = index.knnQueryBatch(data, k=10, num_threads=4)

## Convert base64 string to numpy array
#vstr = base64.decodebytes(b64e)
#vect = np.frombuffer(vstr, dtype=np.int8)


## --------------------------------------

## The following are required:
##   - This file must be named __init__.py
##   - The folder name must match self.name
##   - The class name must be 'Plugin'
##   - The Plugin class must implement the 'analyze' method
##   - The Plugin class must implement the 'debug' method

##   - Please Enjoy and happy searching!!

class Rerank():

    def create_index(self,method,space):
        # initialize a new index, using a HNSW index on Cosine Similarity
        self.index = nmslib.init(method='hnsw', space='cosinesimil')
        self.index.createIndex({'post': 2}, print_progress=False)

    def index_vectors(self,vectors):
        if 'index' in self.keys()
        self.index.addDataPointBatch(vectors)

    def rerank(self,docs:list)->list:
        return vectors

    def debug(self,docs:list)->list:
        return vectors
        
    def __init__(self,metadata):
        self.name="hnsw"
        self.pipeline = metadata
        self.pipeline[self.name] = True
        
        self.index = None
