from math import ceil, floor
import struct
import sys
from functools import partial

class SkipListRetriever:

    def __init__(self, skips_path = "07_skips.bin", vocabulary_path = "07_vocab.bin"):
        self.posting_format = "I"
        self.skips_format = "II"
        self.posting_entry_size = 4
        self.skips_path = skips_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 100
        
        self.SKIP_AMOUNT = 25

        self.__load_vocabulary__()

    def __load_vocabulary__(self):
        self.vocabulary = {}
        try:
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IiH"                         
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)
                
                for binary_info in iter(partial(file.read, chunk_size), b''):                      
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                     
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                    self.vocabulary[term] = [data[0], data[1], data[2]]
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")
            sys.exit(0)

    def load_skip(self, term):                  
        if term in self.vocabulary:            
            index_pointer, skips_pointer, posting_length = self.vocabulary[term]            
            if skips_pointer > -1:
                with open(self.skips_path, "rb") as file:
                    file.seek(skips_pointer)
                    skip_list_size = floor(posting_length / self.SKIP_AMOUNT)
                    data_format = skip_list_size * self.skips_format
                    binary_list = file.read(struct.calcsize(data_format))
                    data = struct.unpack(data_format, binary_list)
                    chunks = [data[x:x+2] for x in range(0, len(data), 2)]
                    return chunks
        return []
    
    def get_vocabulary(self):
        return self.vocabulary



def print_skips(skip_list):
    for entry in skip_list:
        print(f"{entry[0]} {entry[1]}")

def save(dict):
    with open("vocab.txt", "w") as file:
        for key in dict.keys():
            file.write(f"{key} -> {dict[key]}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un término para recuperar su posting")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = SkipListRetriever()    
    else:
        retriever = SkipListRetriever(sys.argv[2], sys.argv[3])

    skips = retriever.load_skip(sys.argv[1])

    print_skips(skips)