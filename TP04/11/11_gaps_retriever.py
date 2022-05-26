import struct
import sys
import pickle
from functools import partial
from BTrees._OOBTree import OOBTree

class GapsListRetriever:

    def __init__(self, index_path = "11_index.bin", vocabulary_path = "11_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path        
        self.VOCAB_TERM_LENGTH = 100

    def load_gaps(self, gaps_pointer, postings_length, total_bytes, gaps_format):
        with open(self.index_path, "rb") as file:
            file.seek(gaps_pointer)
            binary_list = file.read(total_bytes)
            data_format = postings_length * gaps_format
            posting_list = struct.unpack(data_format, binary_list)
            return posting_list


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