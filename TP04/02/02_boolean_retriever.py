from re import S
import struct
import sys
import pickle
from xmlrpc.client import Boolean

class BooleanRetriever:

    ###
    # - Toma el índice de entrada. Recibe una query.
    # - Recupera las postings de cada término a memoria.
    # - Con operaciones de conjuntos (dadas por la query), combinar las postings
    ###

    def __init__(self, index_path = "01_index.idx", vocabulary_path = "01_vocab.pcl"):
        self.posting_format = "I"
        self.posting_entry_size = 4
        self.index_path = index_path
        self.vocabulary_path = vocabulary_path
        self.__load_vocabulary__()
    
        self.AND_OP = "&"
        self.OR_OP = "|"
        self.NEG_OP = "-"

    def __load_vocabulary__(self):
        try:
            with open(self.vocabulary_path, "rb") as file:
                self.vocabulary = pickle.load(file)
        except:
            print(f"No se pudo cargar el vocabulario desde {self.vocabulary_path}")
            sys.exit(0)

    def __load_posting__(self, term):                  
        if term in self.vocabulary:
            posting_length, pointer = self.vocabulary[term]
            with open(self.index_path, "rb") as file:
                file.seek(pointer)
                binary_list = file.read(posting_length * self.posting_entry_size)
                data_format = self.posting_format * posting_length
                posting_list = struct.unpack(data_format, binary_list)
                return set(posting_list)
        else:             
            return set()

    def __is_term__(self, query):
        for character in [self.AND_OP, self.OR_OP, self.NEG_OP, "(", ")"]:
            if character in query:
                return False
        return True
        

    def __process_conjunction__(self, conjunction):
        open_stack = []
        left_side = ""
        i = 0
        
        # Elimina paréntesis de alrededor
        if conjunction.startswith("(") and conjunction.endswith(")"):
            conjunction = conjunction[1:-1]

        for character in conjunction:
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
        operator = conjunction[i-fallback:i+delta]
        right_side = conjunction[i+delta:]
        return left_side.strip(), operator.strip(), right_side.strip()

    def __calc_set_operation__(self, set_a, op, set_b):        
        if (op == self.AND_OP):
            return set_a.intersection(set_b)
        if (op == self.OR_OP):
            return set_a.union(set_b)
        if (op == self.NEG_OP):
            return set_a - set_b

    def __process_query__(self, query):
        # Get left_side, operator, right_side
        if self.__is_term__(query):       
            posting = self.__load_posting__(query)            
            return posting
        
        left_side, operation, right_side = self.__process_conjunction__(query)
        left_side_posting = self.__process_query__(left_side)
        rigth_side_posting = self.__process_query__(right_side)            
        return self.__calc_set_operation__(left_side_posting, operation, rigth_side_posting)
    

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
    
    result = retriever.__process_query__(sys.argv[1])
    print_posting(result)