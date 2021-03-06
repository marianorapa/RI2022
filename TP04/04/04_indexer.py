from math import ceil
from partial_memory_indexer import Indexer
import struct
import sys
import os
import shutil
import time
from heapq import merge

class BooleanPartialIndexer:

    def __init__(self, vocabulary_output_path = "04_vocab.bin", docs_buffer_size = 10):
        self.base_indexer = Indexer()
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_runs_path = "index-runs"
        self.vocabulary_output_path = vocabulary_output_path
        self.vocabulary = {}        
        self.DOCS_BUFFER_SIZE = docs_buffer_size
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
        indexing_start_time = time.time()
        for i in range(0, partitions):
            portion = files[i*self.DOCS_BUFFER_SIZE:min((i+1)*self.DOCS_BUFFER_SIZE, len(files))]
            self.index, self.docs_total_terms = self.base_indexer.index_files(portion, i * self.DOCS_BUFFER_SIZE)
            index_vocab = self.__save_index__(i)
            self.vocabularies.append(index_vocab)
        indexing_end_time = time.time()
        self.indexing_time = indexing_end_time - indexing_start_time
        
        merge_start_time = time.time()
        index_file, vocabulary = self.__merge_runs__()
        merge_end_time = time.time()
        
        self.__rename_index__(index_file)
        self.vocabulary = vocabulary    
        
        self.merge_time = merge_end_time - merge_start_time
        self.__save_vocabulary__()
    
    def __rename_index__(self, file):
        os.rename(file, "04_index.bin")

    def get_index_size(self):
        return len(self.index.keys())

    def get_vocab_size(self):
        return len(self.vocabulary.keys())

    def __save_index__(self, run_number):               
        output_path = self.index_runs_path + f"/index-{run_number}.bin"
        self.indexes_paths.append(output_path)
        pointer = 0
        vocab = {}
        with open(output_path, "wb") as file:
            for term in self.index.keys():
                posting_lists = self.index[term]
                df = len(posting_lists)
                vocab[term] = [df, pointer]
                output_format = df * self.posting_format
                values = [sublist[0] for sublist in posting_lists]                
                packed_postings = struct.pack(output_format, *values)
                bytes_written = file.write(packed_postings)
                pointer += bytes_written                
            self.index_size += len(self.index)
        return vocab

    def __delete_file__(self, file):
        if os.path.exists(file):
            os.remove(file)

    def __merge_runs__(self):           
        remaining_paths = self.indexes_paths
        remaining_vocabs = self.vocabularies
        while len(remaining_paths) > 1:
            new_paths = []
            new_vocabs = []
            for i in range(0, len(remaining_paths), 2):
                file_1 = remaining_paths[i]
                vocab_1 = remaining_vocabs[i]
                if (i+1) >= len(remaining_paths):
                    new_paths.append(file_1)
                    new_vocabs.append(vocab_1)
                    continue         
                file_2 = remaining_paths[i+1]
                vocab_2 = remaining_vocabs[i+1]                
                output_file, output_vocab = self.__merge_2_runs_improved__(file_1, vocab_1, file_2, vocab_2)
                self.__delete_file__(file_1)
                self.__delete_file__(file_2)                
                new_paths.append(output_file)
                new_vocabs.append(output_vocab)
            remaining_paths = new_paths
            remaining_vocabs = new_vocabs            
        return remaining_paths[0], remaining_vocabs[0]
           
    def __merge_2_runs__(self, run_file_1, run_vocab_1, run_file_2, run_vocab_2):
        i, j = 0, 0
        output_file_name = f"04_output-{self.output_file_count}.bin"
        output_file = open(output_file_name, "wb")
        #with open(output_file_name, "wb") as output_file:
        output_vocab = {}
        file_pointer = 0            
        file_1 = open(run_file_1, "rb")
        file_2 = open(run_file_2, "rb")
        print(f"Vocab 1 size {len(run_vocab_1)} and Vocab 2 size {len(run_vocab_2)}")
        #with open(run_file_1, "rb") as file_1:
        #    with open(run_file_2, "rb") as file_2:
        while i < len(run_vocab_1) and j < len(run_vocab_2):
            #print(f"i = {i}; j = {j}")
            term_1, term_1_df, term_1_pointer = self.__get_entry_data_at_position__(i, run_vocab_1)
            term_2, term_2_df, term_2_pointer = self.__get_entry_data_at_position__(j, run_vocab_2)
            output_term = ""
            output_posting = []                        
            if term_1 == term_2:
                output_term = term_1
                i += 1
                j += 1

                # Estoy en el mismo t??rmino, hay que mergear ambas postings                            
                posting_1 = self.__read_posting__(file_1, term_1_pointer, term_1_df)                            
                posting_2 = self.__read_posting__(file_2, term_2_pointer, term_2_df)

                i2, j2 = 0, 0                            
                while i2 < len(posting_1) and j2 < len(posting_2):
                    doc_id_1 = posting_1[i2]
                    doc_id_2 = posting_2[j2]
                    if doc_id_1 < doc_id_2:
                        output_posting.append(doc_id_1)
                        i2 += 1
                    elif doc_id_2 < doc_id_1:
                        output_posting.append(doc_id_2)
                        j2 += 1
                    else:
                        output_posting.append(doc_id_1)
                        i2 += 1
                        j2 += 1
                
                while i2 < len(posting_1):
                    output_posting.append(posting_1[i2])
                    i2 += 1
                while j2 < len(posting_2):
                    output_posting.append(posting_2[j2])
                    j2 += 1
            
            elif term_1 < term_2:
                # Va term_1 al output file, e incremento i
                i += 1
                output_term = term_1
                output_posting = self.__read_posting__(file_1, term_1_pointer, term_1_df)
            else:
                # Va term_2 al output file, e incremento j
                j += 1                            
                output_term = term_2
                output_posting = self.__read_posting__(file_2, term_2_pointer, term_2_df)                            
            
            # Guardo el output al archivo, el t??rmino al vocabulario y aumento el pointer
            file_pointer = self.__save_posting_to_file__(output_posting, output_file, output_term, output_vocab, file_pointer)
            
        # Cuando sale, alguno de los dos vocabularios se qued?? sin t??rminos. Agrego los del otro
        while i < len(run_vocab_1):
            term_1, term_1_df, term_1_pointer = self.__get_entry_data_at_position__(i, run_vocab_1)
            output_posting = self.__read_posting__(file_1, term_1_pointer, term_1_df)
            file_pointer = self.__save_posting_to_file__(output_posting, output_file, term_1, output_vocab, file_pointer)
            i += 1

        while j < len(run_vocab_2):
            term_2, term_2_df, term_2_pointer = self.__get_entry_data_at_position__(j, run_vocab_2)
            output_posting = self.__read_posting__(file_2, term_2_pointer, term_2_df)
            file_pointer = self.__save_posting_to_file__(output_posting, output_file, term_2, output_vocab, file_pointer)
            j += 1

        self.__flush_output_postings__()
        output_file.close()
        file_1.close()
        file_2.close()    

        self.output_file_count += 1
        return output_file_name, output_vocab

    def __get_entry_data_at_position__(self, position, vocab):
        term = list(vocab.keys())[position]
        term_entry = vocab[term]
        term_df = term_entry[0]
        term_pointer = term_entry[1]
        return term, term_df, term_pointer

    def __save_posting_to_file__(self, posting, file, term, vocab, pointer):

        df = len(posting)
        vocab[term] = [df, pointer]
        output_format = df * self.posting_format
        packed_postings = struct.pack(output_format, *posting)
        bytes_written = file.write(packed_postings)
        return pointer + bytes_written

    
    def __read_posting__(self, file, pointer, length):        
        file.seek(pointer)        
        bytes = file.read(length * self.posting_entry_size)                            
        data_format = self.posting_format * length
        return struct.unpack(data_format, bytes)
    
    def __merge_2_runs_improved__(self, run_file_1, run_vocab_1, run_file_2, run_vocab_2):
        i, j = 0, 0
        output_file_name = f"04_output-{self.output_file_count}.bin"
        output_file = open(output_file_name, "wb")
        
        output_vocab = {}
        file_pointer = 0            
        file_1 = open(run_file_1, "rb")
        file_2 = open(run_file_2, "rb")        
           
        combined_keys = sorted(set(list(run_vocab_1.keys()) + list(run_vocab_2.keys())))
        print(len(combined_keys))
        for key in combined_keys:
            key_in_1 = key in run_vocab_1
            key_in_2 = key in run_vocab_2
            if key_in_1 and key_in_2:
                term_1_df, term_1_pointer = run_vocab_1[key]
                term_2_df, term_2_pointer = run_vocab_2[key]
                posting_1 = self.__read_posting__(file_1, term_1_pointer, term_1_df)
                posting_2 = self.__read_posting__(file_2, term_2_pointer, term_2_df)
                output_posting = list(merge(posting_1, posting_2))
                file_pointer = self.__save_posting_to_file__(output_posting, output_file, key, output_vocab, file_pointer)
            elif key_in_1:
                term_1_df, term_1_pointer = run_vocab_1[key]
                output_posting = self.__read_raw_posting__(file_1, term_1_pointer, term_1_df)
                file_pointer = self.__save_raw_posting_to_file__(output_posting, term_1_df, output_file, key, output_vocab, file_pointer)
            elif key_in_2:
                term_2_df, term_2_pointer = run_vocab_2[key]
                output_posting = self.__read_raw_posting__(file_2, term_2_pointer, term_2_df)                            
                file_pointer = self.__save_raw_posting_to_file__(output_posting, term_2_df, output_file, key, output_vocab, file_pointer)
            else:
                print(f"How did this key get in here? {key}")
        output_file.close()
        file_1.close()
        file_2.close()    

        self.output_file_count += 1
        return output_file_name, output_vocab


    def __read_raw_posting__(self, file, pointer, length):        
        file.seek(pointer)        
        return file.read(length * self.posting_entry_size)   

    def __save_raw_posting_to_file__(self, raw_posting, df, file, term, vocab, pointer):
        vocab[term] = [df, pointer]
        bytes_written = file.write(raw_posting)
        return pointer + bytes_written                         
        

    #def __save_vocabulary__(self):
    #    max_term_length = self.base_indexer.get_max_term_length()        
    #    with open(self.vocabulary_output_path, "wb") as file:
    #        for term in self.vocabulary.keys():
    #            try:
    #                df = self.vocabulary[term][0]
    #                pointer = self.vocabulary[term][1]                
    #                term = term + " " * (max_term_length - len(term))
    #                output_format = "IH"                
    #                packed_values = struct.pack(output_format, pointer, df)
    #                encoded_term = term.encode('ascii')
    #                file.write(encoded_term + packed_values)
    #            except:
    #                print(f"Couldn't save term {term}")                
    #    file.close()

    def __save_vocabulary__(self):
        #max_term_length = self.base_indexer.get_max_term_length()        
        max_term_length = self.VOCAB_TERM_LENGTH
        with open(self.vocabulary_output_path, "wb") as file:
            for term in self.vocabulary.keys():
                try:
                    df = self.vocabulary[term][0]
                    pointer = self.vocabulary[term][1]                
                                        
                    output_format = "IH"                
                    packed_values = struct.pack(output_format, pointer, df)                    
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
                except Exception as e:
                    print(f"Couldn't save term {term}: {e}")
        file.close()

    def print_stats(self):
        print(f"Indexing time: {self.indexing_time}")
        print(f"Merging time: {self.merge_time}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Es necesario pasar como argumento un path a un directorio y la cantidad de documentos por ??ndice parcial')
        sys.exit(0)
    docs_buffer_size = int(sys.argv[2])
    indexer = BooleanPartialIndexer(docs_buffer_size=docs_buffer_size)
    indexer.index_dir(sys.argv[1])    
    indexer.print_stats()
    #print(f"Max term length is: {indexer.get_max_term_length()}")        
    print(f"Total indexed docs: {indexer.total_docs}")