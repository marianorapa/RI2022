import time
import math
from memory_indexer import Indexer
import struct
import sys
from compressor import Compressor
from bitarray import bitarray

posting_retriever_lib = __import__("11_postings_retriever")


class FrequencyIndexer:

    def __init__(self):
        self.base_indexer = Indexer()
        self.compressor = Compressor()
        
        self.vocabulary = {}        

        self.index_variable_byte_path = "11_index_variable_byte.bin"
        self.index_gamma_path = "11_index_gamma.bin"
        self.index_gaps_variable_byte_path = "11_index_gaps_variable_byte.bin"
        self.index_gaps_gamma_path = "11_index_gaps_gamma.bin"
        self.vocabulary_gamma_path = "11_vocab_gamma.bin"
        self.vocabulary_gaps_gamma_path = "11_vocab_gaps_gamma.bin"
        self.vocabulary_variable_byte_path = "11_vocab_variable_byte.bin"
        self.vocabulary_gaps_variable_byte_path = "11_vocab_gaps_variable_byte.bin"

        self.posting_retriever = posting_retriever_lib.PostingsListRetriever()
        
        self.VOCAB_TERM_LENGTH = 100         # longer terms will be truncated in vocab
    
    def get_max_term_length(self):
        return self.base_indexer.get_max_term_length()

    def index_dir(self, dir):
        self.index, self.doc_vectors, self.docs_total_terms = self.base_indexer.index_dir(dir)
        #start = time.time()
        #self.save_index(self.index_variable_byte_path, 2)        
        #end = time.time()
        #print(f"Variable Byte compression index saving time: {end - start}")
        #self.__save_vocabulary__(self.vocabulary_variable_byte_path)
        #
        #start = time.time()
        #self.save_index(self.index_gamma_path, 1)        
        #end = time.time()        
        #self.__save_vocabulary__(self.vocabulary_gamma_path)
        #print(f"Gamma compression index saving time: {end - start}")
        #
        ## With gaps
        #start = time.time()
        #self.save_index_with_gaps(self.index_gaps_variable_byte_path, 2)        
        #end = time.time()
        #self.__save_vocabulary__(self.vocabulary_gaps_variable_byte_path)
        #print(f"Variable Byte compression index with gaps saving time: {end - start}")
#
#        #start = time.time()
        #self.save_index_with_gaps(self.index_gaps_gamma_path, 1)        
        #end = time.time()        
        #self.__save_vocabulary__(self.vocabulary_gaps_gamma_path)
        #
        #print(f"Gamma compression index with gaps saving time: {end - start}")       
       

    def load_index_with_loaded_dict(self, index_path, compression_method):
        loaded_index = {}
        for term in self.vocabulary.keys():
            term_pointer, df, total_bytes, right_padding = self.vocabulary[term]
            compressed_posting = self.posting_retriever.load_compressed_posting_from_params(index_path, term_pointer, total_bytes)
            posting = self.compressor.decompress(compressed_posting, compression_method, right_padding)
            loaded_index[term] = posting

            
    def evaluate_posting_retrieval(self):
        self.posting_retriever.load_vocabulary(self.vocabulary_variable_byte_path)
        start = time.time()
        for term in self.vocabulary.keys():
            self.posting_retriever.load_posting(term, self.index_variable_byte_path, compression_method = 2)
        end = time.time()
    
        print(f"Variable Byte index decompression time: {end - start}")

        self.posting_retriever.load_vocabulary(self.vocabulary_variable_byte_path)
        
        start = time.time()
        for term in self.vocabulary.keys():
            self.posting_retriever.load_posting(term, self.index_gamma_path, compression_method = 1)
        end = time.time()        
        
        print(f"Gamma index decompression time: {end - start}")

        self.posting_retriever.load_vocabulary(self.vocabulary_gaps_variable_byte_path)
        start = time.time()
        for term in self.vocabulary.keys():
            self.posting_retriever.load_posting_with_gaps(term, self.index_gaps_variable_byte_path, compression_method = 2)
        end = time.time()
        print(f"Variable Byte index with gaps decompression time: {end - start}")

        self.posting_retriever.load_vocabulary(self.vocabulary_gaps_gamma_path)
        start = time.time()
        for term in self.vocabulary.keys():
            self.posting_retriever.load_posting_with_gaps(term, self.index_gaps_gamma_path, compression_method = 1)
        end = time.time()        

        print(f"Gamma index with gaps decompression time: {end - start}")
        
    def get_index_size(self):
        return len(self.index.keys())

    def get_vocab_size(self):
        return len(self.vocabulary.keys())

    def save_index(self, output_path, compression_method = 1):          
        pointer = 0
        with open(output_path, "wb") as file:
            for term in self.index.keys():
                posting_lists = self.index[term]
                df = len(posting_lists)
                values = [item for sublist in posting_lists for item in sublist]

                compressed, right_padding = self.compressor.compress(values, compression_method)
                output_format = "B" * len(compressed)
                packed_postings = struct.pack(output_format, *compressed)
                bytes_written = file.write(packed_postings)
                self.vocabulary[term] = [df, pointer, bytes_written, right_padding]
                pointer += bytes_written

    def save_index_with_gaps(self, output_path, compression_method = 1):          
        pointer = 0
        with open(output_path, "wb") as file:
            for term in self.index.keys():
                posting_lists = self.index[term]
                df = len(posting_lists)                
                
                previous_doc_id = posting_lists[0][0]
                gaps_lists = []
                gaps_lists.append([previous_doc_id, posting_lists[0][1]])
                for entry in posting_lists[1:]:                    
                    doc_id = entry[0]
                    gaps_lists.append([doc_id - previous_doc_id, entry[1]])
                    previous_doc_id = doc_id
                
                values = [item for sublist in gaps_lists for item in sublist]

                compressed, right_padding = self.compressor.compress(values, compression_method)                
                
                output_format = "B" * len(compressed)
                packed_postings = struct.pack(output_format, *compressed)
                bytes_written = file.write(packed_postings)
                self.vocabulary[term] = [df, pointer, bytes_written, right_padding]
                pointer += bytes_written
    

    def __save_vocabulary__(self, output_path):
        
        max_term_length = self.VOCAB_TERM_LENGTH
        with open(output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df, pointer, bytes, right_padding = self.vocabulary[term]
                                        
                    output_format = "IHHH"                
                    packed_values = struct.pack(output_format, pointer, df, bytes, right_padding)                    
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
       

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    indexer = FrequencyIndexer()
    indexer.index_dir(sys.argv[1])
        
    index_size = indexer.get_index_size()
    print(f"Index size (in terms) is: {index_size}")
    vocab_size = indexer.get_vocab_size()
    if index_size != vocab_size:
        print("Something is wrong with index and vocab size")