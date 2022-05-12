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

# Generates an index (dict) with each term as a key. Values are the posting lists with [doc_id, TF]

class Indexer:

    def __init__(self):

        self.MIN_LENGTH = 3
        self.MAX_LENGTH = 25

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

    def search_files(self, dir, files = [], recursive = True):
        path = pathlib.Path(dir)        
        for item in path.iterdir():            
            if (item.is_file()):                
                files.append(item.absolute())
            else:                
                if (item.is_dir() and recursive):
                    self.search_files(item, files)            

    def __index_doc(self, doc_id, doc, index, docs_terms):        
        try:
            with open(doc, "r", encoding="utf-8") as f:                
                
                tokens = self.tokenizer.get_tokens_with_frequency(f.read())
                docs_terms[doc_id] = [0, doc.stat().st_size]
                for token in tokens.keys():
                    if token not in self.palabras_vacias:
                        if token not in index:
                            index[token] = []
                            if len(token) > self.max_term_length:
                                self.max_term_length = len(token)

                        index[token].append([doc_id, tokens[token]])                         
                        docs_terms[doc_id][0] += 1   # Este documento tiene un término más
                return tokens
        except Exception as e:
            print(f"Error indexing doc {doc}: {e}")

    def get_index(self):
        return self.index

    #def index_dir(self, directory):
    #    self.dir = directory
    #    files = []
    #    self.search_files(directory, files)        
    #    index, docs_total_terms = self.__index_files(files)
    #    self.index = index
    #    return self.index, docs_total_terms

    # Indexing calls
    def index_files(self, files, offset):        
        index = {}
        doc_terms = {}  
        doc_id = 0 + offset
        with open("doc_ids.csv", mode="a", encoding="utf-8") as doc_ids_file:
            for file in files:
                current_file = pathlib.Path(file)
                self.__index_doc(doc_id, current_file, index, doc_terms)
                doc_ids_file.write(f"{current_file.name},{doc_id}\n")
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