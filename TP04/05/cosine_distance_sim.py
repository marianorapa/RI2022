from cmath import log, sqrt
from TFIDF_weighting_scheme import TFIDFWeightingScheme


class CosineDistanceSim:

    def __init__(self, weighting_scheme):
        self.weighting_scheme = weighting_scheme
        

    def retrieve_docs(self, index, query_terms, collection_size):
        scores = {}
        
        candidate_docs = []
        
        # Guardo mayor frecuencia de término en query
        max_freq_query_term = 0
        for term in query_terms.keys():
            if (query_terms[term]) > max_freq_query_term:
                max_freq_query_term = query_terms[term]

        # Precalculo los pesos de cada término en la query 
        # Mergeo las posting lists para tener una lista única de doc ids candidatos. <-------------- TODO: Verificar que no haya repetidas :TODO <-----------------------
        query_weights = {}
        squared_sum_query_weights = 0
        for term in query_terms.keys():
            if (term in index):                
                postings = index[term][1:]
                candidate_docs.extend(postings)     # Mergeo las postings de candidatos                
                term_weight = self.weighting_scheme.calc_query_term_weight(query_terms[term], max_freq_query_term, collection_size, len(index[term]) - 1)                
                print(f"Params are {query_terms[term]}, {max_freq_query_term}, {collection_size}, {len(index[term]) - 1}")
                query_weights[term] = term_weight
                print(f"Term {term} weight in query is {term_weight}")
                squared_sum_query_weights += pow(term_weight, 2)

        sqrt_query_weights = sqrt(squared_sum_query_weights)

        for doc in candidate_docs:
            score = 0

            # Se necesita calcular la raiz de los pesos de los términos del documento al cuadrado            
            numerator_acum = 0
            for term in query_terms:
                term_posting = index[term]
                for entry in term_posting[1:]:
                    if (entry[0] == doc[0]):
                        term_frequency = entry[1]   # Es la frecuencia del término en el documento - Puedo usarla para un score parcial
                        term_weight_in_doc = self.weighting_scheme.calc_doc_term_weight(term_frequency, collection_size, len(term_posting) - 1)                        
                        #print(f"Term {term} weight in doc: {term_weight_in_doc} in doc {doc[0]} for frequency {term_frequency}")
                        print(query_weights[term])
                        numerator_acum += query_weights[term] * term_weight_in_doc

            doc_squared_sum = 0             
            
            for term in index.keys():
                for entry in index[term][1:]:            
                    if entry[0] == doc[0]:
                        term_tfidf = self.weighting_scheme.calc_doc_term_weight(entry[1], collection_size, len(index[term]) - 1)                        
                        doc_squared_sum += pow(term_tfidf, 2)            
            
            
            denominator = sqrt_query_weights * sqrt(doc_squared_sum)

            score = numerator_acum/denominator
            scores[doc[0]] = score
                     
        return scores