from ctypes import pointer
from re import S
import struct
import sys
from functools import partial
from tokenizer import Tokenizer

posting_retriever_lib = __import__("10_postings_retriever")

class BooleanRetriever:

    def __init__(self, index_path = "10_index.bin", vocabulary_path = "10_vocab.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.VOCAB_TERM_LENGTH = 100        
        self.__load_vocabulary__()
        self.tokenizer = Tokenizer(3, 50)

        self.posting_retriever = posting_retriever_lib.PostingsListRetriever()
        
    def __load_vocabulary__(self):
        self.vocabulary = {}
        try:             
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IiI"                         
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)                
                for binary_info in iter(partial(file.read, chunk_size), b''): 
                    try:   
                        term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                                                                       
                        data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                        self.vocabulary[term] = [data[0], data[1], data[2]]
                    except Exception as e:
                        #print(binary_info[:self.VOCAB_TERM_LENGTH])                                   
                        print(e)
                        pass                             

        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")            
            sys.exit(0)

    def __doc_at_a_time__(self, postings):
        pointers = {}
        min_term = list(postings.keys())[0]
        min_doc_id = postings[min_term][0]        
        shortest_posting_term = list(postings.keys())[0]
        shortest_posting_term_size = len(postings[shortest_posting_term])
        for term in postings:
            pointers[term] = 0            
            if len(postings[term]) < shortest_posting_term_size:
                shortest_posting_term = term
                shortest_posting_term_size = len(postings[term])
        result = []

        finished = False
        while not finished:
            same_doc_id = True
            for term in postings.keys():
                term_pointer = pointers[term]
                term_current_doc_id = postings[term][term_pointer]
                if term_current_doc_id < min_doc_id:
                    min_term = term
                    min_doc_id = term_current_doc_id
                    same_doc_id = False
                elif term_current_doc_id > min_doc_id:
                    same_doc_id = False
            
            if same_doc_id:
                result.append(min_doc_id)

            # Actualizo pointers de los menores doc_id
            for term in postings.keys():
                term_pointer = pointers[term]
                term_current_doc_id = postings[term][term_pointer]
                if term_current_doc_id == min_doc_id:                    
                    pointers[term] += 1
                    if len(postings[term]) == pointers[term]:
                        finished = True
                    
            # Cambiar min_doc_id por uno candidato si todavia quedan
            if not finished:
                min_doc_id = postings[min_term][pointers[min_term]]
        
        return result

    def __term_at_a_time__(self, postings):

        partial_result = {}

        first_posting = postings[list(postings.keys())[0]]
        for term in first_posting:
            partial_result[term] = 1

        for term in list(postings.keys())[1:]:
            term_posting = postings[term]
            for doc_id in term_posting:
                if doc_id in partial_result:
                    partial_result[doc_id] += 1

        result = []

        all_postings = len(postings)
        for doc_id in partial_result.keys():
            if partial_result[doc_id] == all_postings:
                result.append(doc_id)

        return sorted(result)

    def process_query(self, query, taat = False):
        terms = self.tokenizer.get_tokens_with_frequency(query)
        postings = {}
        total_postings_size = 0
        for term in terms.keys():
            if term in self.vocabulary:
                postings[term] = self.posting_retriever.load_posting(term)                
                total_postings_size += len(postings[term])
        if len(postings) > 0:
            if taat:
                return self.__term_at_a_time__(postings), total_postings_size
            return self.__doc_at_a_time__(postings), total_postings_size
        return [], total_postings_size
    
def print_posting(posting):
    for doc_id in posting:
        print(f"{doc_id}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio indicar una query entre comillas")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = BooleanRetriever()    
    else:
        retriever = BooleanRetriever(sys.argv[2], sys.argv[3])
    
    result = retriever.process_query(sys.argv[1], taat=False)
    print_posting(result)