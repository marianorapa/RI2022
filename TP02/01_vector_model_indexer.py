from audioop import reverse
import sys
import pathlib
import math

def read_vocabulary(file):
    vocabulary = {}
    with open(file, "r") as f: 
        ignored_line = f.readline()
        for line in f.readlines():
            parts = line.split("\t")
            if len(parts) == 3:
                vocabulary[int(parts[0])] = float(parts[1])
    return vocabulary


def read_document_terms(file):
    document_terms = {}
    with open(file, "r") as f: 
        ignored_line = f.readline()
        for line in f.readlines():
            parts_1 = line.split(":")
            if len(parts_1) == 2:
                doc_id = parts_1[0].split(" ")[1]
                terms = [float(term.strip()) for term in parts_1[1].replace("(", "").replace(")", "").split(",")]                
                document_terms[int(doc_id)] = terms    
    return document_terms

def scalar_product(vector1, vector2, vector1_weights, vector2_weights):
    sum = 0
    for element in vector1:
        if element in vector2:            
            sum += vector1_weights[element] * vector2_weights[element]
    return sum

def calc_query_weights(query_terms, vocabulary):
    result = {}
    for term in query_terms:        
        term_weight = (0.5 + 0.5 * (1)) * float(vocabulary[term])
        result[term] = term_weight
    return result

def calc_doc_weights(doc_terms, vocabulary):    
    result = {}
    for term in doc_terms:
        term_weight = 1 * vocabulary[term]
        result[term] = term_weight
    return result


def sim(query_terms, document_terms, vocabulary):
    query_weights = calc_query_weights(query_terms, vocabulary)
    document_weights = calc_doc_weights(document_terms, vocabulary)
    numerator = scalar_product(query_terms, document_terms, query_weights, document_weights)
    squared_query_weights = 0
    for term in query_weights:
        weight = query_weights[term]
        squared_query_weights += pow(float(weight), 2)
    squared_doc_weights = 0
    for term in document_weights:
        weight = document_weights[term]
        squared_doc_weights += pow(float(weight), 2)
    try:
        return numerator / (math.sqrt(squared_query_weights) * math.sqrt(squared_doc_weights))
    except:        
        return 0
    

# Query: list(id_term)
# Document_terms: {doc_id: list(id_term)}
# Vocabulary: {term_id, idf}
def rank_documents(query, documents_terms, vocabulary):
    ranking = {}
    for doc_id in documents_terms:
        doc_terms = documents_terms[doc_id] # list(id_term)
        score = sim(query, doc_terms, vocabulary)
        if (score > 0):
            ranking[doc_id] = score
    return ranking

if __name__ == '__main__': 
    vocab_file = sys.argv[1]
    document_terms_file = sys.argv[2]
    vocabulary = read_vocabulary(vocab_file)
    documents_terms = read_document_terms(document_terms_file)
    while True:
        query = input("Ingresar query: ")
        query = [int(term) for term in query.split(" ")]
        ranking = rank_documents(query, documents_terms, vocabulary)
        sorted_ranking = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
        for document in sorted_ranking.keys():
            print(f"Doc id: {document}. Score: {sorted_ranking[document]}")
