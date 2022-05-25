import pickle
from memory_indexer import Indexer
import struct
import sys

class BooleanIndexer:

    def __init__(self, index_output_path = "07_index.bin", vocabulary_output_path = "07_vocab.bin", skips_output_path = "07_skips.bin"):
        self.base_indexer = Indexer()
        self.posting_format = "I"
        self.skips_format = "II"
        self.posting_entry_size = 4
        self.index_output_path = index_output_path
        self.vocabulary_output_path = vocabulary_output_path
        self.vocabulary = {}                
        self.skips_output_path = skips_output_path
        
        self.SKIP_AMOUNT = 25

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
        index_pointer = 0
        skips_pointer = 0
        with open(self.index_output_path, "wb") as index_file:
            with open(self.skips_output_path, "wb") as skips_file:                
                for term in self.index.keys():                
                    posting_lists = self.index[term]
                    df = len(posting_lists)
                    self.vocabulary[term] = [df, index_pointer, -1]
                    posting_output_format = df * self.posting_format
                    values = []
                    i = 0
                    skips_list = []    
                    for doc_id in posting_lists:                        
                        i += 1
                        values.append(doc_id[0])
                        if i % self.SKIP_AMOUNT == 0:
                            skips_list.append(doc_id[0])
                            skips_list.append(i)        # Se almacena el indice del doc en la posting, non-zero-based
                    
                    #values = [sublist[0] for sublist in posting_lists]                                         
                    packed_postings = struct.pack(posting_output_format, *values)                    
                    bytes_written = index_file.write(packed_postings)                    
                    index_pointer += bytes_written                    
                    
                    if len(skips_list) > 0:
                        skips_output_format = self.skips_format * int((len(skips_list) / 2))
                        packed_skips = struct.pack(skips_output_format, *skips_list)
                        bytes_written = skips_file.write(packed_skips)
                        self.vocabulary[term][2] = skips_pointer        # Actualiza la posición en el índice
                        skips_pointer += bytes_written


    def __save_vocabulary__(self):
        #max_term_length = self.base_indexer.get_max_term_length()        
        max_term_length = self.VOCAB_TERM_LENGTH
        with open(self.vocabulary_output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df, index_pointer, skips_pointer = self.vocabulary[term]
                                        
                    output_format = "IiH"                             
                    packed_values = struct.pack(output_format, index_pointer, skips_pointer, df)                    
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
    indexer = BooleanIndexer()
    indexer.index_dir(sys.argv[1])    
    index_size = indexer.get_index_size()
    print(f"Index size (in terms) is: {index_size}")
    vocab_size = indexer.get_vocab_size()
    if index_size != vocab_size:
        print("Something is wrong with index and vocab size")  