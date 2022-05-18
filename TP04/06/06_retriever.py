from re import S
import struct
import sys
import pickle
from xmlrpc.client import Boolean
from functools import partial

class LiteralProximityRetriever:

    ###
    # - Toma el índice de entrada. Recibe una query.
    # - Recupera las postings de cada término a memoria.
    # - Con operaciones de conjuntos (dadas por la query), combinar las postings
    ###

    def __init__(self,  index_path = "05_index.bin", vocabulary_path = "05_vocab.bin", positions_path = "05_positions.bin"):
        self.posting_format = "IIH"        
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.positions_path = positions_path
        self.VOCAB_TERM_LENGTH = 50
        self.__load_vocabulary__()

        self.AND_OP = "&"
        self.OR_OP = "|"
        self.NEG_OP = "-"

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
        if term in self.vocabulary:
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
        else:             
            return set()

    def __is_term__(self, query):
        for character in [self.AND_OP, self.OR_OP, self.NEG_OP, "(", ")"]:
            if character in query:
                return False
        return True
        

    def __process_non_terminal__(self, non_terminal):
        open_stack = []
        left_side = ""
        i = 0
        
        # Elimina paréntesis de alrededor
        if non_terminal.startswith("(") and non_terminal.endswith(")"):
            non_terminal = non_terminal[1:-1]

        for character in non_terminal:
            i += 1
            if character == "(":
                if len(left_side) > 0:
                    break
                open_stack.append(1)
            elif character == ")":
                open_stack.pop()
                if (len(open_stack) == 0):               
                    left_side = left_side + character
                    break
            elif character in ["&", "|", "-"]:
                if (len(open_stack) == 0):                    
                    break
            left_side = left_side + character

        delta = 2
        if (character in ["&", "|", "-"]):
            delta = 1
        fallback = 1
        if (character == ")"):
            fallback = 0
        operator = non_terminal[i-fallback:i+delta]
        right_side = non_terminal[i+delta:]
        return left_side.strip(), operator.strip(), right_side.strip()

    def __calc_set_operation__(self, set_a, op, set_b):        
        if type(set_a) == list:
            set_a = set(set_a) 
        if type(set_b) == list:
            set_b = set(set_b) 
        if (op == self.AND_OP):
            return set_a.intersection(set_b)
        if (op == self.OR_OP):
            return set_a.union(set_b)
        if (op == self.NEG_OP):
            return set_a - set_b

    def __process_query__(self, query, first_call = False):
        # Obtener postings de cada término

        # Obtener unión (and de documentos)

        # Verificar con las posiciones de cada documento en un dict (query_terms_positions) si contains_literal_query
        pass
    
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
    
    #result = retriever.__process_query__(sys.argv[1], first_call=True)
    #print_posting(result)    
    print(retriever.__load_posting__(sys.argv[1]))