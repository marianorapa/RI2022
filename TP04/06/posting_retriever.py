import chunk
import struct
import sys
import pickle
from functools import partial

class PostingListRetriever:

    def __init__(self, index_path = "05_index.bin", vocabulary_path = "05_vocab.bin"):
        self.posting_format = "IH"
        self.posting_entry_size = 6
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 50        

    def load_vocabulary(self):
        self.vocabulary = {}
        try:
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IH"               
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)
                for binary_info in iter(partial(file.read, chunk_size), b''):
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                     
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                    self.vocabulary[term] = [data[0], data[1]]
                return self.vocabulary
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path} con data {binary_info}: {e}")
            sys.exit(0)

    def load_posting(self, term):                  
        if term in self.vocabulary:
            pointer, df = self.vocabulary[term]                      
            with open(self.index_path, "rb") as file:
                file.seek(pointer)
                data_format = self.posting_format * df
                binary_list = file.read(struct.calcsize(data_format))
                data = struct.unpack(data_format, binary_list)
                chunks = [data[x:x+2] for x in range(0, len(data), 2)]
                return chunks
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
        print("Es obligatorio un t??rmino para recuperar su posting")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = PostingListRetriever()    
    else:
        retriever = PostingListRetriever(sys.argv[2], sys.argv[3])

    posting = retriever.load_posting(sys.argv[1])

    save(retriever.get_vocabulary())

    print_posting(posting)