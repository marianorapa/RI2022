import pathlib
from tokenizer import Tokenizer
import sys

## Tener en cuenta que guarda el CF del término en la primera posición del arreglo

class Indexer:

    def __init__(self):
        self.MIN_LENGTH = 3
        self.MAX_LENGTH = 25

        self.tokenizer = Tokenizer(self.MIN_LENGTH, self.MAX_LENGTH)
        self.index = {}

        self.palabras_vacias = []

        self.total_docs              = 0
        self.total_tokens            = 0
        self.total_terms             = 0
        self.total_terms_length      = 0

        self.max_term_length = 0

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
                
                for token in tokens.keys():
                    if token not in index:
                        index[token] = [0]
                        if len(token) > self.max_term_length:
                            self.max_term_length = len(token)
                    # Acumulate CF in array's first position   
                    index[token][0] += tokens[token]    
                    index[token].append([doc_id, tokens[token]]) 
                    #docs_terms[doc_id][0] += 1   # Este documento tiene un término más
                return tokens
        except Exception as ex:            
            print(f"Error indexing doc {doc}: {ex}")

    def get_index(self):
        return self.index

    def get_collection_size(self):
        return self.total_docs

    def index_dir(self, directory):
        self.dir = directory
        files = []
        self.__search_files(directory, files)        
        index, doc_terms = self.__index_files(files)
        self.index = index
        return self.index

    # Indexing calls
    def __index_files(self, files):        
        index = {}
        doc_terms = {} 
        doc_id = 1
        for file in files:
            current_file = pathlib.Path(file)
            self.__index_doc(doc_id, current_file, index, doc_terms)            
            doc_id += 1            
        self.total_docs = doc_id - 1
        return index, doc_terms

    def get_terms_from_query(self, query):
        return self.tokenizer.get_tokens_with_frequency(query)


def print_dict(dict):
    for key in dict.keys():
        print(f"{key} -> {dict[key]}")

def print_index_summary(dict):
    for key in dict.keys():
        print(f"{key} -> {len(dict[key]) - 1}")

if __name__ == '__main__':
    indexer = Indexer()
    index = indexer.index_dir(sys.argv[1])    
    print_index_summary(index)