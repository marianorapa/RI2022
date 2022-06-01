import struct
import sys
import pickle
from functools import partial
from BTrees._OOBTree import OOBTree

gaps_list_retriever_lib = __import__('11_gaps_retriever')

class PostingsListRetriever:

    def __init__(self, index_path = "11_index.bin", vocabulary_path = "11_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 100        
        self.gaps_retriever = gaps_list_retriever_lib.GapsListRetriever()

    def load_vocabulary(self):
        #self.vocabulary = {}
        self.vocabulary = OOBTree()
        try:
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IHH"                          
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)
                
                for binary_info in iter(partial(file.read, chunk_size), b''):                      
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                     
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                    self.vocabulary[term] = [data[0], data[1], data[2]]
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")
            sys.exit(0)


    def load_compressed_posting_from_params(self, index_path, term_pointer, total_bytes):
        with open(index_path, "rb") as file:
            file.seek(term_pointer)
            compressed_bytes = file.read(total_bytes)
            data_format = "B" * total_bytes
            compressed_ints = struct.unpack(data_format, compressed_bytes)
            return compressed_ints

    def load_compressed_posting(self, index_path, term):                  
        if term in self.vocabulary:
            #gaps = self.gaps_retriever.load_gaps(term)
            pointer, df, total_bytes = self.vocabulary[term]
            
            # TODO: Descomprimir gaps y devolver lista de postings
            with open(index_path, "rb") as file:
                file.seek(pointer)
                compressed_bytes = file.read(total_bytes)
                data_format = "B" * total_bytes
                compressed_ints = struct.unpack(data_format, compressed_bytes)
                
                return compressed_ints
        return []
   

    def get_vocabulary(self):
        return self.vocabulary



def print_postings(posting):
    for doc_id in posting:
        print(f"{doc_id}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un término para recuperar su gap list")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = PostingsListRetriever()    
    else:
        retriever = PostingsListRetriever(sys.argv[2], sys.argv[3])

    gaps = retriever.load_posting(sys.argv[1])
    print_postings(gaps)