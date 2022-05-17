# Recibe una query y devuelve ranking por modelo vectorial con TF-IDF
import math
import sys
import struct
from memory_indexer import Indexer
from functools import partial
from posting_retriever import PostingListRetriever
class VectorialRetriever:
    
    def __init__(self, index_path = "05_index.bin", vocabulary_path = "05_vocab.bin", docs_norms_path = "05_doc_norms.bin"):
        self.posting_format = "IH"
        self.posting_entry_size = 6
        self.index_path = index_path
        self.indexer = Indexer()
        self.posting_retriever = PostingListRetriever()
        self.vocabulary_path = vocabulary_path
        self.docs_norms_path = docs_norms_path
        self.VOCAB_TERM_LENGTH = 50
        self.__load_vocabulary__()
        self.__load_docs_norm__()
        
    def __load_docs_norm__(self):
        self.docs_norms = {}
        try:
             with open(self.docs_norms_path, "rb") as file:                
                data_format = "If"        
                chunk_size = struct.calcsize(data_format)
                for binary_info in iter(partial(file.read, chunk_size), b''):
                    data = struct.unpack(data_format, binary_info)
                    doc_id = data[0]
                    norm = data[1]
                    self.docs_norms[doc_id] = norm
        except Exception as e:
            print(f"No se pudo cargar la norma de los documentos desde {self.docs_norms_path}: {e}")
            sys.exit(0)

    def __load_vocabulary__(self):
        self.vocabulary = self.posting_retriever.load_vocabulary()

    def __load_posting__(self, term):                  
        return self.posting_retriever.load_posting(term)

    def query(self, query):
        results = {}
        query_terms = self.indexer.get_terms_from_query(query)
                
        query_weights, query_norm = self.__calculate_query_weights_and_norm__(query_terms)
        
        weighted_postings = []
        for term in query_terms:
            if term in self.vocabulary:
                posting = self.__load_posting__(term)
                weighted_postings.append([term, self.__calculate_weighted_posting__(posting)])

        # La posicion que se analiza de cada posting se guarda en un arreglo donde el indice en este mapea con el de la lista de postings
        posting_pointers = []
        for i in range (0, len(query_terms)):
            # Inicializo pointers en 0 i.e me paro al principio de cada posting
            posting_pointers.append(0)
                
        # Mientras que haya punteros que no terminaron la lista en la que están i.e sean distintos a None
        while self.__values_present__(posting_pointers):            
            current_doc = 100000000000000000000 # Inicia current doc en valor alto
            terms_in_current_doc = []
            # Busqueda de documento actual y de terminos del documento actual
            for i in range (0, len(query_terms)):                
                posting_pointer = posting_pointers[i]
                # Chequeo que no se haya terminado esa posting
                if not posting_pointer is None:                    
                    #term = weighted_postings[i][0]                    
                    term_posting = weighted_postings[i][1][posting_pointer]        
                    doc_id = term_posting[0]                    
                    if doc_id < current_doc:                        
                        current_doc = doc_id
                        terms_in_current_doc = [i]  # Se reinicia la lista y se agrega el termino actual
                    elif doc_id == current_doc:
                        terms_in_current_doc.append(i)
            # Tengo armada la lista de terminos de la query que están en el documento que estoy evaluando
            cosine_numerator = 0
            for term_pos in terms_in_current_doc:
                posting_pointer = posting_pointers[term_pos]
                term = weighted_postings[term_pos][0]
                current_posting = weighted_postings[term_pos]
                term_postings = current_posting[1]
                term_posting = term_postings[posting_pointer]
                doc_id = term_posting[0]
                if (doc_id != current_doc):
                    raise Exception("Something is wrong with current doc and the one being added to numerator")
                doc_score = term_posting[1]
                query_term_weight = query_weights[term]
                cosine_numerator += doc_score * query_term_weight            
                # Avanzo los punteros de las postings del documento actual salvo que haya llegado al último elemento y quede None
                if posting_pointer < (len(term_postings) - 1):   
                    posting_pointers[term_pos] = posting_pointers[term_pos] + 1                    
                else:
                    posting_pointers[term_pos] = None
            results[current_doc] = cosine_numerator / (self.docs_norms[current_doc] * query_norm)
                
        sorted_results = sorted(results.items(), key=lambda kv: kv[1], reverse=True)

        return sorted_results



    def __values_present__(self, list):
        for entry in list:
            if not entry is None:
                return True
        return False


    def __calculate_query_weights_and_norm__(self, query_terms):
        output = {}
        max_freq = 0
        squared_sum = 0
        for term in query_terms.keys():
            if query_terms[term] > max_freq:
                max_freq = query_terms[term]
        for term in query_terms.keys():
            frequency = query_terms[term]         
            df = self.vocabulary[term][1]   
            idf = math.log(len(self.vocabulary) / df)            
            output[term] = (0.5 + 0.5 * (frequency/max_freq)) * math.log(idf)
            squared_sum += pow(output[term], 2)            
        return output, math.sqrt(squared_sum)

    def __calculate_weighted_posting__(self, posting):
        df = len(posting)
        idf = math.log(len(self.vocabulary) / df)
        output = []
        for entry in posting:
            doc_id = entry[0]
            tf = entry[1]
            output.append([doc_id, tf * idf])
        return output

def print_results(results):
    for entry in results:
        print(f"{entry[0]} {entry[1]}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Pasar como argumento una query')
        sys.exit(0)
    
    query = sys.argv[1]

    retriever = VectorialRetriever()
    results = retriever.query(query)
    print_results(results)