from math import ceil, sqrt
import struct
import sys
from BTrees._OOBTree import OOBTree

class VocabMaker:

    def __init__(self, postings_path, index_output_path = "08_index.bin", skips_output_path = "08_skips.bin",
     vocabulary_output_path = "08_vocab.bin", skips_k = 3):
        self.postings_path = postings_path
        self.index_output_path = index_output_path
        self.skips_output_path = skips_output_path
        self.SKIPS_K = skips_k
        self.vocabulary = OOBTree()
        self.VOCAB_TERM_LENGTH = 100
        self.vocabulary_output_path = vocabulary_output_path

    def run(self):

        index_file = open(self.index_output_path, "wb")
        skips_file = open(self.skips_output_path, "wb")
        index_pointer = 0
        skips_pointer = 0
        with open(self.postings_path, "r", encoding="utf-8") as postings_file:
            for line in postings_file.readlines():
                line = line.strip()
                term, df, raw_posting = line.split(":")              
                posting = raw_posting.split(",") 
                posting = posting[:-1]              # Eliminar última posición vacía
                posting = [int(x) for x in posting]
                posting = sorted(posting)               
                skips_list = []
                skip_amount = ceil(sqrt(int(df)))
                i = 1                         # i comienza en 1 porque ya pongo un elemento
                last_doc_id = posting[0]
                delta_gaps = [last_doc_id]    # El primer id se agrega tal cual
                for doc_id_string in posting[1:]:
                    doc_id = int(doc_id_string)
                    delta = doc_id - last_doc_id
                    delta_gaps.append(delta)
                    i += 1
                    #if i % self.SKIPS_K == 0:
                    if i % skip_amount == 0:
                        skips_list.append(doc_id)
                        skips_list.append(i)        # no zero-based
                    
                    last_doc_id = doc_id

                # Agregar al vocabulario
                if len(skips_list) > 0:
                    self.vocabulary.insert(term, [int(df), index_pointer, skips_pointer])
                else:    
                    # Si no hay skip list, pongo -1
                    self.vocabulary.insert(term, [int(df), index_pointer, -1])   

                # Agregar al indice
                data_format = "I" * int(df)
                output_gaps = struct.pack(data_format, *delta_gaps)
                bytes_written = index_file.write(output_gaps)
                index_pointer += bytes_written

                # Agregar a las skips
                if len(skips_list) > 0:
                    data_format = "I" * len(skips_list)
                    output_skips = struct.pack(data_format, *skips_list)
                    bytes_written = skips_file.write(output_skips)
                    skips_pointer += bytes_written

        self.__save_vocabulary__()

    def __save_vocabulary__(self):
        max_term_length = self.VOCAB_TERM_LENGTH
        with open(self.vocabulary_output_path, "wb") as file:
            for pair in self.vocabulary.iteritems(): 
                term = pair[0]
                df, index_pointer, skips_pointer = pair[1]                
                                                        
                output_format = "IiI"
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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a las postings')
        sys.exit(0)
    postings_path = sys.argv[1]
    indexer = VocabMaker(postings_path)
    indexer.run()
