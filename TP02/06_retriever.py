from calendar import c
import sys
import pathlib
import os
import re
import time
import math

palabras_vacias = []

MIN_LENGTH = 3
MAX_LENGTH = 25

total_docs              = 0
total_tokens            = 0
total_terms             = 0
total_terms_length      = 0

# -------------------------------------------
# Indexing functions
# -------------------------------------------
def get_proper_names(line):
    regex = "((?<!\A)(?<!(?:\.\s))(?:(?:(?:[A-Z][a-z]+)+)(?:[ ]*(?:[A-Z][a-z]+))*)[^\.])"        # Won't consider proper names after a ". " since it could mean the start of a sentence
    result = re.findall(regex, line)
    
    return list(filter(lambda x: x.lower() not in palabras_vacias and len(x) >= MIN_LENGTH and len(x) <= MAX_LENGTH,
                                     [x.strip() for x in result])) 
    
def is_date(token):
    regex = "(\d+[\/\.\-]\d+[\/\.\-]\d+)"
    return bool(re.match(regex, token))

def get_numbers(token):
    regex = "([\+\-]?(?:[0-9]+[,\-]?)*[0-9](?:[.][0-9]+)?)"     # accepts some form of telephone numbers and also numbers starting with + or -
    return re.findall(regex, token)

def get_abbreviations(token, collection):    
    regex_1 = "(?:\A|\W)(?:[a-zA-Z](?:\.[a-zA-Z])+)(?:\Z|\W)"             # matches "i.e", "i.e.", "u.s.a", etc
    regex_2 = "(?:[A-Z][bcdfghj-np-tvxz]+\.)"                             # extracted from article, matches capital letter followed by consonants
    regex_3 = "(?:^|\W)(?:[A-Z]{2,5})(?:$|\W)"                            # matches abbreviations as capital letters with initials like NASA or JFK
    regex_4 = "(?:(?:^|\W)[bcdfghj-np-tvxz]{2,4}\.)"                      # matches all consonants ending in period
    regex_5 = "(?:[A-Z][aeiou][bcdfghj-np-tvxz]\.)"                       # matches "Lic.", "Mag."
    regex_6 = "(?:^|\W)(?:[a-zA-Z]{1,2}(?:\.[a-zA-Z]{1,2})+)(?:$|\W)"
    exists_without_last_period = False
    exists_lower = False
    if (re.match("[A-Za-z]+\.", token)):
        exists_without_last_period = token[:-1] in collection       # if it ends with period, checks if it's in the collection without it
    if (re.match("[A-Z]+", token)):
        exists_lower = token.lower() in collection
    if not exists_without_last_period and not exists_lower:
        return re.findall(f"{regex_1}|{regex_2}|{regex_3}|{regex_4}|{regex_5}|{regex_6}", token)

def is_mail_or_url(token):
    url_regex = "([A-Za-z]+:/+[A-Za-z0-9_\-\.]+\.[A-Za-z0-9_\-\./]+[^https:])"        # takes into account when there are 2 urls sticked together
    url_regex_2 = "(www\.[a-z0-9]+(?:\.[a-z]{2,4}){1,4})"
    mail_regex = "([A-Za-z0-9_\-\.]+@[A-Za-z]+(?:\.[A-Za-z]+)+)"
    return bool(re.match(f"{url_regex}|{mail_regex}|{url_regex_2}", token))

def remove_punctuation(token):
    return re.sub("[\W_]", "", token)

def get_tokens_and_freq_in_line(line, tokens_freq, collection_terms, update_collection = True):
    line = translate(line).strip()              
    # Intentar identificar nombres propios 
    proper_names = get_proper_names(line)
    for name in proper_names: 
        # Elimina los nombres identificados para que no sean tomados como tokens al separar por espacios
        line.replace(name, "")
        name = name.lower()
        tokens_freq[name] = 1 if (name not in tokens_freq) else (tokens_freq[name] + 1)
        if update_collection:
            collection_terms[name] = 1 if (name not in collection_terms) else (collection_terms[name] + 1)        

    tokens_list = line.strip().split()
    special_token = False
    for token in tokens_list:                
        numbers = get_numbers(token)                    
        if (len(numbers) > 0):
            token = numbers[0]
            tokens_list.extend(numbers[1:])
            special_token = True
        elif (is_mail_or_url(token)):                                                      
            special_token = True
        else:
            abbreviations = get_abbreviations(token, collection_terms)
            if (abbreviations and len(abbreviations) > 0):
                token = abbreviations[0]
                tokens_list.extend(abbreviations[1:])
            elif (not is_date(token)):
                token = remove_punctuation(token)
                token = translate(token.lower())     
        token_length_ok = (len(token) >= MIN_LENGTH) and (len(token) <= MAX_LENGTH)
        if special_token or ((not special_token) and (token not in palabras_vacias) and token_length_ok):                                                
            tokens_freq[token] = 1 if (token not in tokens_freq) else (tokens_freq[token] + 1)    
            if update_collection:
                collection_terms[token] = 1 if (token not in collection_terms) else (collection_terms[token] + 1)    
    return line

def get_tokens_and_freq(doc, collection_terms):
    tokens_freq = {}    
    try:
        with open(doc, "r", encoding="utf-8") as f:                
            for line in f.readlines():                 
                get_tokens_and_freq_in_line(line, tokens_freq, collection_terms)
            return tokens_freq
    except Exception as e:
        print(f"Error getting tokens from file {doc}: {e}")


def translate(to_translate):
	tabin = u'áäâàãéëèêẽíïĩìîóõöòôúüùûũ'
	tabout = u'aaaaaeeeeeiiiiiooooouuuuu'
	tabin = [ord(char) for char in tabin]
	translate_table = dict(zip(tabin, tabout))
	return to_translate.translate(translate_table)


def read_palabras_vacias(path):
    output = []
    with open(path, "r") as f: 
        for line in f.readlines():
            stop_words = line.split(",")
            output.append(stop_words)
    return [item for sublist in output for item in sublist]

def search_files(dir, files = [], recursive = True):
    path = pathlib.Path(dir)
    for item in path.iterdir():
        if (item.is_file()):
            files.append(item.absolute())
        else:
            if (item.is_dir() and recursive):
                search_files(item, files)            

# Indexing calls
def index_files(files):    
    collection_terms = {}
    docs = {}
    for file in files:
        current_file = pathlib.Path(file)        
        docs[current_file.name] = get_tokens_and_freq(current_file, collection_terms)
    return docs, collection_terms



# -------------------------------------------
# Retrieval functions
# -------------------------------------------

def calculate_term_weight_in_query(term, frequency, collection_terms):
    # (1+log(Fiq)) * log(N/ni)    
    if (term in collection_terms):
        return (1 + frequency) * math.log(len(collection_terms)/collection_terms[term])
    return 0
    
def calculate_query_weights(query, collection_terms):
    weights = {}
    query_tokens = {}    
    get_tokens_and_freq_in_line(query, query_tokens, collection_terms, False)       
    for token in query_tokens:
        weights[token] = calculate_term_weight_in_query(token, query_tokens[token], collection_terms)

    return weights


def calculate_doc_weights_tfidf(doc_frequencies, collection_terms): 
    weights = {}
    for term in doc_frequencies:
        tfidf = (1 + math.log(doc_frequencies[term])) * math.log(len(collection_terms)/collection_terms[term])
        weights[term] = tfidf
    
    return weights

def calculate_doc_weights(doc_name, doc_frequencies, precalc_doc_weights, collection_terms):
    if (doc_name in precalc_doc_weights):
        return precalc_doc_weights[doc_name]
    
    doc_weights = calculate_doc_weights_tfidf(doc_frequencies, collection_terms)

    precalc_doc_weights[doc_name] = doc_weights
    return doc_weights

def cosine_distance(query_weights, doc_weights):    
    numerator = 0
    squared_query_sum = 0
    squared_docs_sum = 0
    
    keys = set(query_weights.keys()).union(set(doc_weights.keys()))
    
    for key in keys:
        query_weight = 0 if not key in query_weights else query_weights[key]
        doc_weight = 0 if not key in doc_weights else doc_weights[key]
        numerator += query_weight * doc_weight
        squared_query_sum += math.pow(query_weight, 2)
        squared_docs_sum += math.pow(doc_weight, 2)
    
    denominator = (math.sqrt(squared_query_sum) * math.sqrt(squared_docs_sum))
    if (denominator > 0):
        return numerator / denominator
    return 0

def sim(query, doc_name, doc_frequencies, collection_terms):    
    query_weights = calculate_query_weights(query, collection_terms)        
    doc_weights = calculate_doc_weights(doc_name, doc_frequencies, {}, collection_terms)    
    return cosine_distance(query_weights, doc_weights)

def retrieve_docs(query, doc_collection_frequencies, collection_terms):
    result = {}
    for doc in doc_collection_frequencies:
        score = sim(query, doc, doc_collection_frequencies[doc], collection_terms)
        if score > 0:
            result[doc] = score        
    return result
    

# ----- Saving

def save_index(dict):
    path = "02_index_output.txt"
    with open(path, "w", encoding="utf-8") as f:                
        for key in dict:
            f.write(f"{key} {dict[key]}\n")
    
# -------------------------------------------
# Main
# -------------------------------------------

if __name__ == '__main__':
    start = time.time()
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    dirpath = sys.argv[1]         
    if len(sys.argv) == 3:        
        palabras_vacias = read_palabras_vacias(sys.argv[2])
        print(palabras_vacias)
    if not os.path.exists("./output_02"):
        os.mkdir("./output_02")   
    
    files = []
    search_files(dirpath, files)
    print("Files to be indexed: ")
    for file in files: 
        print(f"{file}\n") 

    doc_collection_frequencies, collection_terms = index_files(files)
    end = time.time()    
    print("\r\nIndexing time: {} seconds.".format(end - start))
    save_index(doc_collection_frequencies)
    
    while True:
        query = input("Enter query:")
        retrieved_docs = retrieve_docs(query, doc_collection_frequencies, collection_terms)
        print("--------- Results ---------")        
        ordered = dict(sorted(retrieved_docs.items(), key=lambda item: item[1], reverse=True))
        for key in ordered.keys():
            print(f"Doc: {key} - Score: {ordered[key]}")
    
    