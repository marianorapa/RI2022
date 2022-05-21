from calendar import c
from pydoc import doc
import pathlib
import pickle as pickle
from tokenizer import Tokenizer

# Generates an index (dict) with each term as a key. Values are the posting lists with [doc_id, TF]

class Indexer:

    def __init__(self):

        self.MIN_LENGTH = 3
        self.MAX_LENGTH = 30

        self.tokenizer = Tokenizer(self.MIN_LENGTH, self.MAX_LENGTH, proper_name_splitting=True)
        self.index = {}

        self.palabras_vacias = []

        self.total_docs              = 0
        self.total_tokens            = 0
        self.total_terms             = 0
        self.total_terms_length      = 0
        
        self.max_term_length = 0


    def get_max_term_length(self):
        return self.max_term_length

    def __read_palabras_vacias(self, path):
        output = []
        with open(path, "r") as f: 
            for line in f.readlines():
                stop_words = line.split(",")
                output.append(stop_words)
        return [item for sublist in output for item in sublist]

    def __search_files(self, dir, files = [], recursive = True):
        path = pathlib.Path(dir)        
        for item in path.iterdir():            
            if (item.is_file()):                
                files.append(item.absolute())
            else:                
                if (item.is_dir() and recursive):
                    self.__search_files(item, files)            

    def __index_doc(self, doc_id, doc, index, docs_terms):        
        try:
            with open(doc, "r", encoding="utf-8") as f:                
                
                tokens = self.tokenizer.get_tokens_with_frequency(f.read())
                docs_terms[doc_id] = [0, doc.stat().st_size]
                for token in tokens.keys():
                    if token not in self.palabras_vacias:
                        if token not in index:
                            index[token] = {}
                            if len(token) > self.max_term_length:
                                self.max_term_length = len(token)
                        if doc_id not in index[token]:
                            index[token][doc_id] = []    
                        
                        positions = tokens[token][1]
                        
                        index[token][doc_id] = positions

                        docs_terms[doc_id][0] += 1   # Este documento tiene un término más
                return tokens
        except Exception as e:
            print(f"Error indexing doc {doc}: {e}")

    def get_index(self):
        return self.index

    def index_dir(self, directory):
        self.dir = directory
        files = []
        self.__search_files(directory, files)        
        index, doc_vectors, docs_total_terms = self.__index_files(files)
        self.index = index
        return self.index, doc_vectors, docs_total_terms

    # Indexing calls
    def __index_files(self, files):        
        index = {}
        doc_terms = {}
        doc_id = 1
        doc_vectors = {}
        with open("doc_ids.csv", mode="w", encoding="utf-8") as doc_ids_file:
            for file in files:
                current_file = pathlib.Path(file)
                tokens = self.__index_doc(doc_id, current_file, index, doc_terms)
                doc_vectors[doc_id] = tokens
                doc_ids_file.write(f"{current_file.name},{doc_id}\n")
                doc_id += 1            
            self.total_docs = doc_id - 1
        return index, doc_vectors, doc_terms

    def get_terms_from_query(self, query, grouping):
        return self.tokenizer.get_tokens_as_list(query, )

    # ----- Saving

    def __save_index(self, dict):
        path = self.dir + "index.pcl"
        with open(path, "wb") as f:                
            pickle.dump(dict, f)