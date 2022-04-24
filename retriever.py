from ast import Index
from calendar import c
from pydoc import doc
import pathlib
import math
import pickle as pickle
from cosine_distance_sim import CosineDistanceSim
from indexer import Indexer
from TFIDF_weighting_scheme import TFIDFWeightingScheme


class Retriever:

    def __init__(self, indexer):
        self.indexer = indexer
        self.index = indexer.get_index()
        self.sim_calculator = CosineDistanceSim(TFIDFWeightingScheme())        

    def __load_queries(self, path):
        queries = {}
        path = pathlib.Path(path)    
        with open(path, "r") as f:
            query_count = 1
            for line in f.readlines():
                if (line.startswith("<TITLE>")):
                    line = line.replace("<TITLE>", "").strip()
                    queries[query_count] = line
                    query_count += 1
        return queries

    # -------------------------------------------
    # Retrieval functions
    # -------------------------------------------

    def __cosine_distance(self, query_weights, doc_weights):    
        numerator = 0
        squared_query_sum = 0
        squared_docs_sum = 0
        
        keys = set(query_weights.keys()).union(set(doc_weights.keys()))
        
        for key in keys:
            query_weight = 0 if not key in query_weights else query_weights[key]
            doc_weight = 0 if not key in doc_weights else doc_weights[key]
            numerator += query_weight * doc_weight
            squared_query_sum += math.pow(query_weight, 2)
            squared_docs_sum += math.pow(doc_weight, 2)
        
        denominator = (math.sqrt(squared_query_sum) * math.sqrt(squared_docs_sum))
        if (denominator > 0):
            return numerator / denominator
        return 0

    def retrieve_docs(self, query):
        scores = {}
        # The index has term frequencies in each doc. TF-IDF is pending        
        query_terms = self.indexer.get_terms_from_query(query)
        collection_size = self.indexer.get_collection_size()
        scores = self.sim_calculator.retrieve_docs(self.index, query_terms, collection_size)
        print(scores)
      
    def load_index_from_file(file):
        return pickle.load(file)
