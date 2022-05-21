import struct
import sys
from functools import partial
from memory_indexer import Indexer

class LiteralProximityRetriever:

    ###
    # - Toma el índice de entrada. Recibe una query.
    # - Recupera las postings de cada término a memoria.
    # - Con operaciones de conjuntos (dadas por la query), combinar las postings
    ###

    def __init__(self,  index_path = "06_index.bin", vocabulary_path = "06_vocab.bin", positions_path = "06_positions.bin"):
        self.posting_format = "IIH"        
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.positions_path = positions_path
        
        self.indexer = Indexer()

        self.VOCAB_TERM_LENGTH = 50
        self.__load_vocabulary__()

        self.PROXIMITY_OP = "cerca_de"

    def __load_vocabulary__(self):
        self.vocabulary = {}
        try:
             with open(self.vocabulary_path, "rb") as file:       
                chunk_size = self.VOCAB_TERM_LENGTH + 6
                for binary_info in iter(partial(file.read, chunk_size), b''):                      
                    data_format = "IH"                         
                    term = binary_info[:self.VOCAB_TERM_LENGTH].decode("ascii").strip()                                
                    data = struct.unpack(data_format, binary_info[self.VOCAB_TERM_LENGTH:])    
                    self.vocabulary[term] = [data[0], data[1]]                

        except Exception as e:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}: {e}")
            sys.exit(0)

    def __load_posting__(self, term):                  
        pointer, posting_length = self.vocabulary[term]                        
        with open(self.index_path, "rb") as file:
            with open(self.positions_path, "rb") as positions_file:
                data_format = self.posting_format * posting_length
                file.seek(pointer)
                #binary_list = file.read(posting_length * posting_entry_size)
                binary_list = file.read(struct.calcsize(data_format))
                posting_list = struct.unpack(data_format, binary_list)
                chunks = [posting_list[x:x+3] for x in range(0, len(posting_list), 3)]
                result = {}
                for chunk in chunks:
                    # chunk es una tripla formada por doc_id, pointer a posiciones, y tf
                    doc_id = chunk[0]
                    pos_pointer = chunk[1]
                    tf = chunk[2]
                    data_format = tf * "H"
                    positions_file.seek(pos_pointer)
                    binary_positions = positions_file.read(struct.calcsize(data_format))
                    result[doc_id] = list(struct.unpack(data_format, binary_positions))
                return result

    def __process_phrase_query__(self, query):
        # Obtener postings de cada término
        terms = self.indexer.get_terms_from_query(query, grouping=False)
        postings = {}             
        min_posting = -1        
        min_term = ""
        for term in terms:
            if term in self.vocabulary:
                postings[term] = self.__load_posting__(term)
                if min_posting == -1 or len(postings[term]) < min_posting:
                    min_posting = len(postings[term])
                    min_term = term
            else:
                return []   # Si un término no está en el vocabulario, la frase no existe
        # Obtener documentos candidatos (que poseen todos los términos)
        candidate_docs = []        
        for doc_id in postings[min_term].keys():
            candidate = True
            for term in terms:
                if doc_id not in postings[term]:
                    candidate = False
                    break
            if candidate:
                candidate_docs.append(doc_id)
        print(f"Candidate docs are {candidate_docs}")
        result = []
        for doc_id in candidate_docs:
            phrase_ok = True
            for i in range(0, len(terms) - 1):
                term_a = terms[i]
                term_b = terms[i+1]
                term_a_positions = postings[term_a][doc_id]
                term_b_positions = postings[term_b][doc_id]
                contiguous = self.__contiguous_terms__(term_a_positions, term_b_positions)
                if not contiguous:
                    phrase_ok = False
                    break
            if phrase_ok:
                result.append(doc_id)
        # Verificar con las posiciones de cada documento en un dict (query_terms_positions) si contains_literal_query
        return result

    def __process_proximity_query__(self, query):
        pass

    def __process_normal_query__(self, query):
        return []

    def __process_query__(self, query, first_call = False):
        # parsear proximidad
        if query.startswith("'") and query.endswith("'"):
            return self.__process_phrase_query__(query)
        if self.PROXIMITY_OP in query:
            return self.__process_proximity_query__(query)
        
        return self.__process_normal_query__(query)
       
    
    def __contains_literal_query__(self, query_terms_positions):
        for first_list_pos in query_terms_positions.keys()[0]:		# Voy por las posiciones del primer término		
            previous_position = first_list_pos	
            for key in query_terms_positions.keys()[1:]:		# Voy por las demás keys			
                # Para esta key me fijo si encuentro una posicion consecutiva
                positions = query_terms_positions[key]
                consecutives = False
                for position in positions:
                    if position == previous_position + 1:
                        consecutives = True
                        previous_position = position
                        break			# Del tercer for
                if not consecutives:
                    break # Del segundo for - No encontré consecutiva -> sigo con la proxima posicion de la primera fila (main for)                
            
            return True # si sigo acá porque no hubo break es que encontré todas las consecutivas
        
        return False


    def __contiguous_terms__(self, term_a_positions, term_b_positions, distance = 1, abs_value = False):
        pointer_a = 0
        pointer_b = 0
        while pointer_a < len(term_a_positions) and pointer_b < len(term_b_positions):
            pos_a = term_a_positions[pointer_a]
            pos_b = term_b_positions[pointer_b]
            
            # Calculate function with given params
            if abs_value:
                pos_distance = abs(pos_b - pos_a)
            else:
                pos_distance = pos_b - pos_a
            if pos_distance > 0 and pos_distance <= distance:
                return True
            else:
                if pos_a < pos_b:
                    pointer_a += 1
                elif pos_b <= pos_a:
                    pointer_b += 1
                #else:
                #    pointer_a +=1
                #    pointer_b += 1
        return False        

def print_posting(posting):
    for doc_id in posting:
        print(f"{doc_id}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio indicar una query entre comillas")
        sys.exit(0)
    if len(sys.argv) < 4:        
        retriever = LiteralProximityRetriever()    
    else:
        retriever = LiteralProximityRetriever(sys.argv[2], sys.argv[3])
    
    result = retriever.__process_query__(sys.argv[1], first_call=True)
    print_posting(result)    
    