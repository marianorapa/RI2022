from ctypes import pointer
from re import S
import struct
import sys
from functools import partial
from memory_indexer import Indexer

posting_retriever_lib = __import__("07_posting_retriever")
skips_retriever_lib = __import__("07_skip_retriever")

class BooleanRetriever:

    def __init__(self, index_path = "07_index.bin", vocabulary_path = "07_vocab.bin", skips_path = "07_skips.bin"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.VOCAB_TERM_LENGTH = 100        
        self.__load_vocabulary__()
        self.indexer = Indexer()
        
        self.posting_retriever = posting_retriever_lib.PostingListRetriever()
        
        self.skips_retriever = skips_retriever_lib.SkipListRetriever()
        
    def __load_vocabulary__(self):
        self.vocabulary = {}
        try:             
             with open(self.vocabulary_path, "rb") as file:       
                data_format = "IiH"                         
                chunk_size = self.VOCAB_TERM_LENGTH + struct.calcsize(data_format)                
                for binary_info in iter(partial(file.read, chunk_size), b''): 
                    try:   
                        term = binary_info[:self.VOCAB_TERM_LENGTH].decode("utf-8").strip()                                                                       
                        data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])
                        self.vocabulary[term] = [data[0], data[1], data[2]]
                    except:
                        print(binary_info[:self.VOCAB_TERM_LENGTH])                                   
        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")            
            sys.exit(0)


    def __intersection_with_skips__(self, postings, skips):
        pointers = {}        
        shortest_posting_term = list(postings.keys())[0]
        shortest_posting_term_size = len(postings[shortest_posting_term])
        for term in postings:
            pointers[term] = 0            
            if len(postings[term]) < shortest_posting_term_size:
                shortest_posting_term = term
                shortest_posting_term_size = len(postings[term])
        result = []

        min_term = list(postings.keys())[0]
        min_doc_id = postings[min_term][0]
 

        finished = False
        while not finished:
            #max_term = min_term
            max_doc_id = min_doc_id
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
                    if term_current_doc_id > max_doc_id:
                        #max_term = term
                        max_doc_id = term_current_doc_id

            if same_doc_id:
                result.append(min_doc_id)

            # Actualizo pointers de los menores doc_id
            for term in postings.keys():
                term_pointer = pointers[term]
                term_current_doc_id = postings[term][term_pointer]
                if term_current_doc_id == min_doc_id and min_doc_id == max_doc_id:                    
                    pointers[term] += 1
                    if len(postings[term]) == pointers[term]:
                        finished = True
                elif term_current_doc_id < max_doc_id:
                    # Adelantar este puntero hasta una posicion de la skip mayor o igual al max_doc_id (si existe, más uno si no)
                    next_pointer = pointers[term] + 1
                    if len(postings[term]) == next_pointer:
                        finished = True
                    else:
                        previous_entry = None                        
                        for entry in skips[term]:
                            if entry[0] >= max_doc_id:                                
                                if previous_entry is not None:                                        
                                    skip_candidate = previous_entry[1]
                                    if skip_candidate > pointers[term]:     # Chequeo que la skip no me indique un doc id menor al previo
                                        next_pointer = skip_candidate
                                    break
                            else:
                                # Cuando me paso 
                                previous_entry = entry    
                    pointers[term] = next_pointer                    
            
            # Cambiar min_doc_id por uno candidato si todavia quedan
            if not finished:                
                min_doc_id = postings[min_term][pointers[min_term]]
        
        return result

    def __intersection__(self, postings):
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

    def process_query(self, query, use_skips = False):
        terms = self.indexer.get_terms_from_query(query)
        postings = {}
        skips = {}
        for term in terms.keys():
            if term in self.vocabulary:
                postings[term] = self.posting_retriever.load_posting(term)
                if use_skips:
                    skips[term] = self.skips_retriever.load_skip(term)
                    return self.__intersection_with_skips__(postings, skips)
                return self.__intersection__(postings)
            else:
                return []
    
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
    
    result = retriever.process_query(sys.argv[1], use_skips=True)
    print_posting(result)