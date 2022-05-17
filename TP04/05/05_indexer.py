import math
from memory_indexer import Indexer
import struct
import sys

class FrequencyIndexer:

    def __init__(self, index_output_path = "05_index.bin", vocabulary_output_path = "05_vocab.bin", doc_norms_output_path = "05_doc_norms.bin"):
        self.base_indexer = Indexer()
        self.posting_format = "IH"
        self.posting_entry_size = 6
        self.index_output_path = index_output_path
        self.vocabulary_output_path = vocabulary_output_path
        self.doc_norms_output_path = doc_norms_output_path
        self.vocabulary = {}        
        
        self.VOCAB_TERM_LENGTH = 50         # longer terms will be truncated in vocab
    
    def get_max_term_length(self):
        return self.base_indexer.get_max_term_length()

    def index_dir(self, dir):
        self.index, self.doc_vectors, self.docs_total_terms = self.base_indexer.index_dir(dir)
        self.__save_index__()        
        self.__save_vocabulary__()
        self.__calculate_and_save_docs_norm_by_tf__()
    
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
       

    def __calculate_and_save_docs_norm_by_tf__(self):           
        doc_norms = {}
        for doc_id in self.doc_vectors.keys():
            doc_vector = self.doc_vectors[doc_id]
            sum = 0
            for term in doc_vector.keys():
                tf = doc_vector[term]
                idf = math.log(len(self.vocabulary) / self.vocabulary[term][0])
                sum += pow(tf*idf, 2)
            doc_norms[doc_id] = math.sqrt(sum)
        with open(self.doc_norms_output_path, "wb") as file:
            for doc_id in doc_norms.keys():
                try:
                    norm = doc_norms[doc_id]                                        
                    output_format = "If"                
                    packed_values = struct.pack(output_format, doc_id, norm)                    
                    file.write(packed_values)
                except:
                    print(f"Couldn't save term {doc_id}'s norm")                
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