import struct
import sys
import pickle
from functools import partial
from BTrees._OOBTree import OOBTree

class GapsListRetriever:

    def __init__(self, index_path = "08_index.bin", vocabulary_path = "08_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 100
        self.__load_vocabulary__()

    def __load_vocabulary__(self):
        #self.vocabulary = {}
        self.vocabulary = OOBTree()
        try:
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IiI"                         
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)
                
                for binary_info in iter(partial(file.read, chunk_size), b''):                      
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                     
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                    self.vocabulary[term] = [data[0], data[1], data[2]]
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")
            sys.exit(0)

    def load_gaps(self, term):                  
        if term in self.vocabulary:
            index_pointer, skips_pointer, posting_length = self.vocabulary[term]            
            with open(self.index_path, "rb") as file:
                file.seek(index_pointer)
                binary_list = file.read(posting_length * self.posting_entry_size)
                data_format = self.posting_format * posting_length
                posting_list = struct.unpack(data_format, binary_list)
                return posting_list
        else: 
            return []
    
    def get_vocabulary(self):
        return self.vocabulary



def print_gaps(posting):
    for doc_id in posting:
        print(f"{doc_id}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un término para recuperar su gap list")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = GapsListRetriever()    
    else:
        retriever = GapsListRetriever(sys.argv[2], sys.argv[3])

    gaps = retriever.load_gaps(sys.argv[1])

    print_gaps(gaps)