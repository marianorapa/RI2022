from math import ceil
import pickle
from partial_memory_indexer import Indexer
import struct
import sys
import os
import shutil

class BooleanPartialIndexer:

    def __init__(self, vocabulary_output_path = "04_vocab.bin"):
        self.base_indexer = Indexer()
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_runs_path = "index-runs"
        self.vocabulary_output_path = vocabulary_output_path
        self.vocabulary = {}        
        self.DOCS_BUFFER_SIZE = 100
        self.VOCAB_TERM_LENGTH = 100
        self.pointer = 0
        self.total_docs = 0
        self.index_size = 0
        self.vocabularies = []
        self.output_file_count = 0
        self.indexes_paths = []
    
    def get_max_term_length(self):
        return self.base_indexer.get_max_term_length()

    def index_dir(self, dir):
        files = []
        self.base_indexer.search_files(dir, files=files)
        self.total_docs = len(files)
        if os.path.exists(self.index_runs_path):
            shutil.rmtree(self.index_runs_path)
        os.mkdir(self.index_runs_path)
        partitions = ceil(len(files) / self.DOCS_BUFFER_SIZE)
        for i in range(0, partitions):
            portion = files[i*self.DOCS_BUFFER_SIZE:min((i+1)*self.DOCS_BUFFER_SIZE, len(files))]
            self.index, self.docs_total_terms = self.base_indexer.index_files(portion, i * self.DOCS_BUFFER_SIZE)
            self.__save_index__(i)
            self.vocabularies.append(self.vocabulary)
        #self.__merge_runs__(partitions)
        #self.__save_vocabulary__()
    
    def get_index_size(self):
        return len(self.index.keys())

    def get_vocab_size(self):
        return len(self.vocabulary.keys())

    def __save_index__(self, run_number):               
        output_path = self.index_runs_path + f"/index-{run_number}.bin"
        self.indexes_paths.append(output_path)
        with open(output_path, "wb") as file:
            for term in self.index.keys():
                posting_lists = self.index[term]
                df = len(posting_lists)
                self.vocabulary[term] = [df, self.pointer]
                output_format = df * self.posting_format
                values = [sublist[0] for sublist in posting_lists]
                packed_postings = struct.pack(output_format, *values)
                bytes_written = file.write(packed_postings)
                self.pointer += bytes_written
            self.index_size += len(self.index)
    
    def __delete_file__(self, file):
        if os.path.exists(file):
            shutil.rmtree(file)

    def __merge_runs__(self):           
        remaining_paths = self.indexes_paths
        remaining_vocabs = self.vocabularies            
        while len(remaining_paths) > 1:
            new_paths = []
            new_vocabs = []
            for i in range(0, len(remaining_paths), 2):
                file_1 = remaining_paths[i]
                vocab_1 = remaining_vocabs[i]
                if (i+1) > len(remaining_paths):
                    new_paths.append(file_1)
                    new_vocabs.append(vocab_1)
                    continue                    
                file_2 = remaining_paths[i+1]
                vocab_2 = remaining_vocabs[i+1]
                output_file, output_vocab = self.__merge_2_runs__(file_1, vocab_1, file_2, vocab_2)
                self.__delete_file__(file_1)
                self.__delete_file__(file_2)
                new_paths.append(output_file)
                new_vocabs.append(output_vocab)
            remaining_paths = new_paths
            remaining_vocabs = new_vocabs
        return remaining_paths[0], remaining_vocabs[0]
           
    def __merge_2_runs__(self, run_file_1, run_vocab_1, run_file_2, run_vocab_2):
        i, j = 0
        with open(f"04_output-{self.output_file_count}", "wb") as output_file:
            output_vocab = {}
            output_file_pointer = 0
            with open(run_file_1, "rb") as file_1:
                with open(run_file_2, "rb") as file_2:
                    
                    while i < len(run_vocab_1) and j < len(run_vocab_2):
                        term_1 = run_vocab_1.keys()[i]
                        term_1_entry = run_vocab_1[term_1]
                        term_1_df = term_1_entry[0]
                        term_1_pointer = term_1_entry[1]
                        
                        term_2 = run_vocab_2.keys()[j]
                        term_2_entry = run_vocab_2[term_2]
                        term_2_df = term_2_entry[0]
                        term_2_pointer = term_2_entry[1]

                        if term_1 == term_2:
                            # Estoy en el mismo término, hay que mergear ambas postings:
                            # Leer la posting del término 1
                            posting_1 = self.__read_posting__(file_1, term_1_pointer, term_1_df)
                            # Leer la posting del término 2
                            posting_2 = self.__read_posting__(file_2, term_2_pointer, term_2_df)
                            
                            pass
                        elif term_1 < term_2:
                            # Va term_1 al output file, e incremento i
                            pass
                        else:
                            # Va term_2 al output file, e incremento j
                            pass
        self.output_file_count += 1
        return output_file, output_vocab

    
    def __read_posting__(self, file, pointer, length):
        file.seek(pointer)
        bytes = file.read(length * self.posting_entry_size)                            
        data_format = self.posting_format * length
        return struct.unpack(data_format, bytes)

    def __save_vocabulary__(self):
        max_term_length = self.base_indexer.get_max_term_length()        
        with open(self.vocabulary_output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df = self.vocabulary[term][0]
                    pointer = self.vocabulary[term][1]                
                    term = term + " " * (max_term_length - len(term))
                    output_format = "IH"                
                    packed_values = struct.pack(output_format, pointer, df)
                    encoded_term = term.encode('ascii')
                    file.write(encoded_term + packed_values)
                except:
                    print(f"Couldn't save term {term}")                
        file.close()
        
    def save_stats(self):        
        posting_sizes = {}
        for term in self.vocabulary:
            term_posting_size = self.vocabulary[term][0] * self.posting_entry_size
            posting_sizes[term_posting_size] = 1 if term_posting_size not in posting_sizes else posting_sizes[term_posting_size] + 1           

        with open("01_stats_posting_list_sizes.csv", "w") as file:
            file.write("posting_list_size,frequency\n")
            for size in posting_sizes.keys():
                file.write(f"{size},{posting_sizes[size]}\n")
        
        with open("01_stats_overhead_docs.csv", "w") as file:
            file.write("doc_id,posting_entries_size,doc_size_bytes\n")
            for doc in self.docs_total_terms.keys():
                file.write(f"{doc},{self.docs_total_terms[doc][0] * self.posting_entry_size},{self.docs_total_terms[doc][1]}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    indexer = BooleanPartialIndexer()
    indexer.index_dir(sys.argv[1])    
    
    indexer.save_stats()
    print(f"Max term length is: {indexer.get_max_term_length()}")
    index_size = indexer.get_index_size()
    print(f"Index size (in terms) is: {index_size}")
    vocab_size = indexer.get_vocab_size()
    print(f"Total indexed docs: {indexer.total_docs}")