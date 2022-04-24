from cmath import log

class TFIDFWeightingScheme:

    def __init__(self):
        self.log_base = 10

    def calc_doc_term_weight(self, term_frequency, collection_size, document_frequency):        
        #return (1 + log(term_frequency, self.log_base)) * log(collection_size/document_frequency, self.log_base)
        return term_frequency * log(collection_size/document_frequency, self.log_base)
    
    def calc_query_term_weight(self, term_frequency, max_term_frequency, collection_size, document_frequency):
        return (0.5 + 0.5 * (term_frequency / max_term_frequency)) / log(collection_size/document_frequency, self.log_base)
        #return (1 + log(term_frequency, self.log_base)) * log(collection_size/document_frequency, self.log_base)
        