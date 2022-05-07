import struct
import sys
import pickle
from functools import partial

class PostingListRetriever:

    def __init__(self, index_path = "01_index.bin", vocabulary_path = "01_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 82
        self.__load_vocabulary__()

    def __load_vocabulary__(self):
        self.vocabulary = {}
        try:
             with open(self.vocabulary_path, "rb") as file:       
                chunk_size = self.VOCAB_TERM_LENGTH + 6
                for binary_info in iter(partial(file.read, chunk_size), b''):                      
                    data_format = "IH"                         
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("ascii").strip()                     
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                    self.vocabulary[term] = [data[0], data[1]]
                print(self.get_vocabulary())
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")            
            sys.exit(0)

    def load_posting(self, term):                  
        if term in self.vocabulary:
            pointer, posting_length = self.vocabulary[term]            
            with open(self.index_path, "rb") as file:
                file.seek(pointer)
                binary_list = file.read(posting_length * self.posting_entry_size)
                data_format = self.posting_format * posting_length
                posting_list = struct.unpack(data_format, binary_list)
                return posting_list
        else: 
            return []
    
    def get_vocabulary(self):
        return self.vocabulary



def print_posting(posting):
    for doc_id in posting:
        print(f"{doc_id}")

def save(dict):
    with open("vocab.txt", "w") as file:
        for key in dict.keys():
            file.write(f"{key} -> {dict[key]}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un término para recuperar su posting")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = PostingListRetriever()    
    else:
        retriever = PostingListRetriever(sys.argv[2], sys.argv[3])

    posting = retriever.load_posting(sys.argv[1])

    save(retriever.get_vocabulary())

    print_posting(posting)