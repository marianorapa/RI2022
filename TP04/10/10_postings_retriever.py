import struct
import sys
import pickle
from functools import partial
from BTrees._OOBTree import OOBTree

gaps_list_retriever_lib = __import__('10_gaps_retriever')

class PostingsListRetriever:

    def __init__(self, index_path = "10_index.bin", vocabulary_path = "10_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 100
        self.__load_vocabulary__()
        self.gaps_retriever = gaps_list_retriever_lib.GapsListRetriever()

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

    def load_posting(self, term):                  
        if term in self.vocabulary:
            gaps = self.gaps_retriever.load_gaps(term)
            result = [gaps[0]]
            for i in range(1, len(gaps)):
                result.append(result[i-1] + gaps[i])
            return result
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