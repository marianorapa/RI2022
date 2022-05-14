import pickle
from memory_indexer import Indexer
import struct
import sys

class BooleanIndexer:

    def __init__(self, index_output_path = "05_index.bin", vocabulary_output_path = "05_vocab.bin"):
        self.base_indexer = Indexer()
        self.posting_format = "IH"
        self.posting_entry_size = 6
        self.index_output_path = index_output_path
        self.vocabulary_output_path = vocabulary_output_path
        self.vocabulary = {}        
        
        self.VOCAB_TERM_LENGTH = 100
    
    def get_max_term_length(self):
        return self.base_indexer.get_max_term_length()

    def index_dir(self, dir):
        self.index, self.docs_total_terms = self.base_indexer.index_dir(dir)
        self.__save_index__()
        self.__save_vocabulary__()
    
    def get_index_size(self):
        return len(self.index.keys())

    def get_vocab_size(self):
        return len(self.vocabulary.keys())

    def __save_index__(self):          
        pointer = 0
        with open(self.index_output_path, "wb") as file:
            for term in self.index.keys():
                posting_lists = self.index[term]
                df = len(posting_lists)
                self.vocabulary[term] = [df, pointer]
                output_format = df * self.posting_format                
                values = [item for sublist in posting_lists for item in sublist]
                packed_postings = struct.pack(output_format, *values)
                bytes_written = file.write(packed_postings)
                pointer += bytes_written
    
    def __save_vocabulary__(self):
        max_term_length = self.base_indexer.get_max_term_length()        
        with open(self.vocabulary_output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df = self.vocabulary[term][0]
                    pointer = self.vocabulary[term][1]                
                    term = term + " " * (max_term_length - len(term))
                    output_format = "IH"                
                    packed_values = struct.pack(output_format, pointer, df)
                    encoded_term = term.encode('ascii')
                    file.write(encoded_term + packed_values)
                except:
                    print(f"Couldn't save term {term}")                
        file.close()
       
  

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    indexer = BooleanIndexer()
    indexer.index_dir(sys.argv[1])    
    
    print(f"Max term length is: {indexer.get_max_term_length()}")
    index_size = indexer.get_index_size()
    print(f"Index size (in terms) is: {index_size}")
    vocab_size = indexer.get_vocab_size()
    if index_size != vocab_size:
        print("Something is wrong with index and vocab size")