import pickle
from memory_indexer import Indexer
import struct
import sys

class BooleanIndexer:

    def __init__(self, index_output_path = "01_index.idx", vocabulary_output_path = "01_vocab.vcb"):
        self.base_indexer = Indexer()
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_output_path = index_output_path
        self.vocabulary_output_path = vocabulary_output_path
        self.vocabulary = {}        
        
        self.VOCAB_TERM_LENGTH = 50
    
    def index_dir(self, dir):
        self.index, self.docs_total_terms = self.base_indexer.index_dir(dir)
        self.__save_index__()
        self.__save_vocabulary__()
    
    def __save_index__(self):          
        pointer = 0
        with open(self.index_output_path, "wb") as file:
            for term in self.index.keys():                
                posting_lists = self.index[term]
                df = len(posting_lists)
                self.vocabulary[term] = [df, pointer]
                output_format = df * self.posting_format
                values = [sublist[0] for sublist in posting_lists]             
                packed_postings = struct.pack(output_format, *values)
                bytes_written = file.write(packed_postings)
                pointer += bytes_written
    
    def __save_vocabulary__(self):
        with open(self.vocabulary_output_path, "wb") as file:
            #pickle.dump(self.vocabulary, file)            
            for term in self.vocabulary.keys():
                df = self.vocabulary[term][0]
                pointer = self.vocabulary[term][1]
                term = term + " " * (self.VOCAB_TERM_LENGTH - len(term))
                output_format = "IH"                
                packed_values = struct.pack(output_format, pointer, df)
                print(term.encode('ascii'))
                file.write(term.encode('ascii'))
                file.write(packed_values)    

    def save_stats(self):        
        posting_sizes = {}
        for term in self.vocabulary:
            term_posting_size = self.vocabulary[term][0] * self.posting_entry_size
            posting_sizes[term_posting_size] = 1 if term_posting_size not in posting_sizes else posting_sizes[term_posting_size] + 1           

        with open("01_stats_posting_list_sizes.csv", "w") as file:
            file.write("posting_list_size,frequency\n")
            for size in posting_sizes.keys():
                file.write(f"{size},{posting_sizes[size]}\n")
        
        with open("01_stats_overhead_docs.csv", "w") as file:
            file.write("doc_id,posting_entries_size,doc_size_bytes\n")
            for doc in self.docs_total_terms.keys():
                file.write(f"{doc},{self.docs_total_terms[doc][0] * self.posting_entry_size},{self.docs_total_terms[doc][1]}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    indexer = BooleanIndexer()
    indexer.index_dir(sys.argv[1])
    indexer.save_stats()