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
        skip_pointers = {}

        result = []

        if len(postings) == 1:
            for term in postings:
                return postings[term]        
        
        #print(postings)
        #print(skips)

        for term in postings:            
            pointers[term] = 0            
            skip_pointers[term] = 0
            #if len(postings[term]) < shortest_posting_term_size:
            #    shortest_posting_term = term
            #    shortest_posting_term_size = len(postings[term])
        

        finished = False
        
        max_term = list(postings.keys())[0]
        max_doc_id = postings[max_term][0]
        while not finished:
            #max_doc_id = min_doc_id
            same_doc_id = True
            #print(f"Now max doc id is {max_doc_id}")
            for term in postings.keys():                
                term_pointer = pointers[term]
                if term_pointer >= len(postings[term]):
                    finished = True
                    break

                term_current_doc_id = postings[term][term_pointer]                
                #print(term_current_doc_id)
                #input()
                if term_current_doc_id > max_doc_id:
                    #print(f"Found doc id {term_current_doc_id} greater than max {max_doc_id}")
                    max_term = term
                    max_doc_id = term_current_doc_id
                    same_doc_id = False
                elif term_current_doc_id < max_doc_id:
                    same_doc_id = False
                    #if term_current_doc_id < min_doc_id:
                    #    min_doc_id = term_current_doc_id

            if same_doc_id:
                #print(f"All terms in same doc id {max_doc_id}. Appending to result")                
                result.append(max_doc_id)    
                #print(result)
                pointers[max_term] += 1     # Avanzo el puntero del término max_term. Cualquiera alcanzaría
            #else:
                #print("Not all terms at same doc id")

            # Actualizo pointers de los menores doc_id
            for term in postings.keys():
                term_pointer = pointers[term]                
                if len(postings[term]) <= pointers[term]:                    
                    finished = True
                    break
                term_current_doc_id = postings[term][term_pointer]
                #print(f"Term {term} is at position {term_pointer} with current doc_id {term_current_doc_id}")
                #if term_current_doc_id == max_doc_id: #and min_doc_id == max_doc_id: 
                #    print("Doc id is the same than looked for")
                #    pointers[term] += 1                    
                #    if len(postings[term]) <= pointers[term]:
                #        print("Here")
                #        finished = True
                if term_current_doc_id < max_doc_id:
                    #print(f"Doc id ({term_current_doc_id}) is smaller than looked for id ({max_doc_id})")
                    # Adelantar este puntero hasta una posicion de la skip mayor o igual al max_doc_id (si existe, más uno si no)
                    next_pointer = pointers[term] + 1
                    if len(postings[term]) <= next_pointer:
                        finished = True
                    elif len(skips[term]) > 0:  
                        
                        skip_pointer = skip_pointers[term] # pointer de la skip actual      
                        if skip_pointer < len(skips[term]):                            
                            #print("Skip list still has unseen values")
                            current_skip_entry = skips[term][skip_pointer]
                            current_skip_doc_id = current_skip_entry[0]
                            current_skip_pos = current_skip_entry[1]
                            previous_skip_doc_id = current_skip_doc_id
                            previous_skip_pos = current_skip_pos - 1

                            # Itero por la skip hasta encontrar un documento que supere al máximo o terminar la lista de skips
                            while current_skip_doc_id <= max_doc_id :
                                
                                # Avanzar en la skip                            
                                previous_skip_pos = current_skip_pos - 1 # zero-based
                                previous_skip_doc_id = current_skip_doc_id
                                skip_pointer += 1
                                if skip_pointer == len(skips[term]):
                                    #print(f"Reached last skip pointer")
                                    break
                                current_skip_doc_id, current_skip_pos = skips[term][skip_pointer]
                            #print(f"Previous skip doc id {previous_skip_doc_id} <= max_doc_id {max_doc_id}")
                            #print(f"Current skip doc id {current_skip_doc_id} > max_doc_id {max_doc_id}")
                            if skip_pointer == len(skips[term]):
                                #print(f"Indeed it's the last skip pointer. Candidate pointer: {next_pointer}")
                                # Estoy en la última posición de las skips y su doc id es menor al máximo
                                next_pointer = max(next_pointer, current_skip_pos - 1)                                                          
                                #print(f"Next pointer is {next_pointer} since it's the max compared to {current_skip_pos - 1}")
                            elif previous_skip_doc_id <= max_doc_id:                            
                                next_pointer = previous_skip_pos
                                #skip_pointer -= 1   # Retrocedo el pointer porque 
                                #print(f"Found better doc id: {previous_skip_doc_id} in skip list. Now pointer is {next_pointer} and doc id {postings[term][next_pointer]}. Skip pointer is at {skip_pointer}")
                            
                            #if (skip_pointers[term] != skip_pointer):
                                #print(f"Updated skip pointer with value {skip_pointer}")
                            skip_pointers[term] = skip_pointer
                            

                    pointers[term] = next_pointer
                    #print(next_pointer)
                    if len(postings[term]) <= next_pointer:
                        #print("Next pointer is term's posting length")
                        finished = True                                     
            
            # Cambiar min_doc_id por uno candidato si todavia quedan
            #if not finished: 
            #    if pointers[min_term] < len(postings[min_term]):
            #        min_doc_id = postings[min_term][pointers[min_term]]
            #    else:
            #        finished = True
       

        return result

    def __intersection__(self, postings):
        pointers = {}
        
        result = []

        if len(postings) == 1:
            for term in postings:
                return postings[term]      
        
        min_term = list(postings.keys())[0]
        min_doc_id = postings[min_term][0]        
        shortest_posting_term = list(postings.keys())[0]
        shortest_posting_term_size = len(postings[shortest_posting_term])
        for term in postings:
            pointers[term] = 0            
            if len(postings[term]) < shortest_posting_term_size:
                shortest_posting_term = term
                shortest_posting_term_size = len(postings[term])
        

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
        total_postings_length = 0
        query_len = len(terms)
        for term in terms.keys():
            if term in self.vocabulary:
                postings[term] = self.posting_retriever.load_posting(term)                
                if use_skips:
                    skips[term] = self.skips_retriever.load_skip(term)
                total_postings_length += len(postings[term])
        if len(postings) > 0:
            if use_skips:
                return self.__intersection_with_skips__(postings, skips), total_postings_length, query_len
            return self.__intersection__(postings), total_postings_length, query_len
        return [], total_postings_length, query_len
    
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
    
    docs, total_postings_length, query_len = retriever.process_query(sys.argv[1], use_skips=True)    
    print_posting(docs)