from memory_indexer import Indexer
import struct
import sys
import pickle

class PostingListRetriever:

    def __init__(self, index_path = "01_index.idx", vocabulary_path = "01_vocab.pcl"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.__load_vocabulary__()

    def __load_vocabulary__(self):
        try:
            with open(self.vocabulary_path, "rb") as file:
                self.vocabulary = pickle.load(file)
        except:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}")
            sys.exit(0)

    def load_posting(self, term):                  
        if term in self.vocabulary:
            posting_length, pointer = self.vocabulary[term]
            with open(self.index_path, "rb") as file:
                file.seek(pointer)
                binary_list = file.read(posting_length * self.posting_entry_size)
                data_format = self.posting_format * posting_length
                posting_list = struct.unpack(data_format, binary_list)
                return posting_list
        else: 
            return []


def print_posting(posting):
    for doc_id in posting:
        print(f"{doc_id}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un término para recuperar su posting")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = PostingListRetriever()    
    else:
        retriever = PostingListRetriever(sys.argv[2], sys.argv[3])
    
    posting = retriever.load_posting(sys.argv[1])

    print_posting(posting)