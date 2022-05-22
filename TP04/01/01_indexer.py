import pickle
from memory_indexer import Indexer
import struct
import sys

class BooleanIndexer:

    def __init__(self, index_output_path = "01_index.bin", vocabulary_output_path = "01_vocab.bin"):
        self.base_indexer = Indexer()
        self.posting_format = "I"
        self.posting_entry_size = 4
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
                values = [sublist[0] for sublist in posting_lists]             
                packed_postings = struct.pack(output_format, *values)
                bytes_written = file.write(packed_postings)
                pointer += bytes_written
    
    #def __save_vocabulary__(self):
    #    max_term_length = self.base_indexer.get_max_term_length()        
    #    with open(self.vocabulary_output_path, "wb") as file:
    #        for term in self.vocabulary.keys():
    #            try:
    #                df = self.vocabulary[term][0]
    #                pointer = self.vocabulary[term][1]                
    #                term = term + " " * (max_term_length - len(term))
    #                output_format = "IH"                
    #                packed_values = struct.pack(output_format, pointer, df)
    #                encoded_term = term.encode('ascii')
    #                file.write(encoded_term + packed_values)
    #            except:
    #                print(f"Couldn't save term {term}")                
    #    file.close()

    def __save_vocabulary__(self):
        #max_term_length = self.base_indexer.get_max_term_length()        
        max_term_length = self.VOCAB_TERM_LENGTH
        with open(self.vocabulary_output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df = self.vocabulary[term][0]
                    pointer = self.vocabulary[term][1]                
                                        
                    output_format = "IH"                
                    packed_values = struct.pack(output_format, pointer, df)                    
                    encoded_term = term.encode('utf-8')
                    
                    if len(encoded_term) > max_term_length:
                        encoded_term = encoded_term[:max_term_length]
                    else:
                        # Fill with spaces
                        encoded_term = encoded_term + (" " * (max_term_length - len(encoded_term))).encode("utf-8")                        
                    written_bytes = file.write(encoded_term)                    
                    written_bytes += file.write(packed_values)
                    if written_bytes != (self.VOCAB_TERM_LENGTH + struct.calcsize(output_format)):
                        print(f"Error: written bytes {written_bytes} defer from expected size {self.VOCAB_TERM_LENGTH + struct.calcsize(output_format)} for term {term} with length {len(term)} and entry {struct.calcsize(output_format)}")
                except Exception as e:
                    print(f"Couldn't save term {term}: {e}")
        file.close()
        
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
    #print(f"Max term length is: {indexer.get_max_term_length()}")
    index_size = indexer.get_index_size()
    print(f"Index size (in terms) is: {index_size}")
    vocab_size = indexer.get_vocab_size()
    if index_size != vocab_size:
        print("Something is wrong with index and vocab size")