from ast import Index
from calendar import c
from pydoc import doc
import sys
import pathlib
import os
import re
import time
import math
import pickle as pickle
from tokenizer import Tokenizer

class Indexer:

    def __init__(self):
        
        self.tokenizer = Tokenizer()
        self.index = {}

        self.palabras_vacias = []

        self.MIN_LENGTH = 3
        self.MAX_LENGTH = 25

        self.total_docs              = 0
        self.total_tokens            = 0
        self.total_terms             = 0
        self.total_terms_length      = 0

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
                print("Nope")
                if (item.is_dir() and recursive):
                    self.__search_files(item, files)            

    def __index_doc(self, doc_id, doc, index, docs_terms):        
        try:
            with open(doc, "r", encoding="utf-8") as f:                
                
                tokens = self.tokenizer.get_tokens_with_frequency(f.read())
                
                for token in tokens.keys():
                    if token not in index:
                        index[token] = [0]
                    # Acumulate CF in array's first position   
                    index[token][0] += tokens[token]    
                    index[token].append([doc_id, tokens[token]])
                    #if doc_id not in docs_terms:
                    #    docs_terms[doc_id] = {}
                    #if token not in docs_terms[doc_id]:
                    #    docs_terms[doc_id][token] = 0
                    #docs_terms[doc_id][token] += 1 
                return tokens
        except Exception as e:
            print(f"Error indexing doc {doc}: {e}")

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
        doc_terms = {}  # Not used
        doc_id = 1
        for file in files:
            current_file = pathlib.Path(file)
            self.__index_doc(doc_id, current_file, index, doc_terms)
            print(f"{current_file.name} -> id: {doc_id}")
            doc_id += 1            
        self.total_docs = doc_id - 1
        return index, doc_terms

    def get_terms_from_query(self, query):
        return self.tokenizer.get_tokens_with_frequency(query)

    # ----- Saving

    def __save_index(self, dict):
        path = self.dir + "index.pcl"
        with open(path, "wb") as f:                
            pickle.dump(dict, f)

        
    def __save_results(self, results):
        path = "output_06_inverted/results.txt"
        with open(path, "w", encoding="utf-8") as f:
            for key in results.keys():
                pos = 0
                for entry in results[key]:
                    f.write(f"{key} Q0 {entry} {pos} {results[key][entry]}\n")
                    pos += 1