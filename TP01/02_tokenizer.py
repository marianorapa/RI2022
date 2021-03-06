import sys
import pathlib
import os
import re
import time

palabras_vacias = []
deep_abbrv_process = False

MIN_LENGTH = 3
MAX_LENGTH = 25

total_docs              = 0
total_tokens            = 0
total_terms             = 0
total_terms_length      = 0
tokens_in_shortest_doc  = 10000
terms_in_shortest_doc   = 10000
tokens_in_longest_doc   = 0
terms_in_longest_doc    = 0
terms_with_freq_one     = 0

abbreviations_list      = []
numbers_list            = []
proper_names_list       = []
mails_urls_list         = []

# -------------------------------------------
def process_dir(filepath):
    frequencies = count_frequencies(filepath)
    save_terms(frequencies)    
    save_collection_stats()
    save_top_last_10_frequencies(frequencies)
    #print_lists()
    save_lists()

def get_proper_names(line):
    #regex = "((?<!\A)(?<!(?:\.\s))(?:(?:(?:[A-Z][a-z]+)+)(?:[ ]*(?:[A-Z][a-z]+))*)[^\.])"        # Won't consider proper names after a ". " since it could mean the start of a sentence
    regex = "((?:(?:[A-Z](?:[a-z]+|\.+))+(?:\s[A-Z][a-z]+)+))"
    result = re.findall(regex, line)
        
    return list(filter(lambda x: x.lower() not in palabras_vacias and len(x) >= MIN_LENGTH,
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
    return re.sub("[^\w\s]|_", "", token)

def count_frequencies(dirpath):
    
    global total_docs
    global total_tokens
    global total_terms
    global total_terms_length
    global tokens_in_shortest_doc
    global terms_in_shortest_doc
    global tokens_in_longest_doc
    global terms_in_longest_doc
    global abbreviations_list
    global numbers_list
    global proper_names_list
    global mails_urls_list
    
    # "casa": [collection_freq, doc_freq]
    frequencies = {}    
    corpus_path = pathlib.Path(dirpath)

    for in_file in corpus_path.iterdir():
        total_docs += 1
        total_doc_tokens = 0
        total_doc_terms  = 0
        document_terms = []
        with open(in_file, "r", encoding="utf-8") as f:                
            for line in f.readlines():  
                line = translate(line).strip()              
                # Intentar identificar nombres propios 
                proper_names = get_proper_names(line)                
                for name in proper_names: 
                    # Elimina los nombres identificados para que no sean tomados como tokens al separar por espacios
                    line.replace(name, "")
                    proper_names_list.append(name)
                                    
                tokens_list = line.strip().split()
                
                # Agrego los nombres propios a la lista de tokens para que tengan el mismo tratamiento
                tokens_list.extend(proper_names)

                for raw_token in tokens_list:                    
                    total_doc_tokens += 1
                    total_tokens     += 1
                    
                    token = raw_token.strip()                                   
                    special_token = False                       
                    numbers = get_numbers(raw_token)                    
                    if (len(numbers) > 0):
                        token = numbers[0]
                        tokens_list.extend(numbers[1:])
                        numbers_list.extend(numbers)
                    elif (is_mail_or_url(raw_token)):
                        mails_urls_list.append(raw_token)                                            
                        special_token = True
                    else:
                        abbreviations = get_abbreviations(raw_token, frequencies)
                        if (abbreviations and len(abbreviations) > 0):
                            abbreviations_list.extend(abbreviations)                            
                        # Las abreviaciones detectadas se eliminan del raw_token
                        if deep_abbrv_process:
                            for abbrv in abbreviations_list:
                                raw_token.replace(abbrv, "")
                        if (not is_date(raw_token)):
                            token = remove_punctuation(raw_token)
                            token = translate(token.lower())                    
                    if special_token or ((not special_token) and (token not in palabras_vacias) and (len(token) >= MIN_LENGTH) and (len(token) <= MAX_LENGTH)):                                                
                        if token in frequencies.keys():
                            frequencies[token] = [frequencies[token][0] + 1, frequencies[token][1]]             # Aumenta CF                       
                        else: # Si es la primera vez que veo este token, se agrega a los t??rminos
                            # DF se inicializa en 0 porque a continuaci??n se incrementa por primera vez
                            frequencies[token] = [1, 0]         
                            total_terms += 1
                            total_terms_length += len(token)
                        # Si es la primera vez que aparece el token en el documento
                        if token not in document_terms:             
                            total_doc_terms += 1
                            document_terms.append(token)
                            frequencies[token] = [frequencies[token][0], frequencies[token][1] + 1]            # Aumenta DF    
            # Comparo los tokens del documento para ver si es el m??s corto o el m??s largo hasta el momento
            if (total_doc_tokens < tokens_in_shortest_doc):
                tokens_in_shortest_doc = total_doc_tokens
                terms_in_shortest_doc = total_doc_terms
            elif (total_doc_tokens > tokens_in_longest_doc):
                tokens_in_longest_doc = total_doc_tokens
                terms_in_longest_doc = total_doc_terms
    return frequencies


def translate(to_translate):
	tabin = u'???????????????????????????????????????????????????'
	tabout = u'aaaaaeeeeeiiiiiooooouuuuu'
	tabin = [ord(char) for char in tabin]
	translate_table = dict(zip(tabin, tabout))
	return to_translate.translate(translate_table)


def save_terms(frequencies):
    global terms_with_freq_one
    with open("output_02/terminos.txt", "w", encoding="utf-8") as f:
        for key in sorted(frequencies):
            try:
                f.write(f'{key} {frequencies[key][0]} {frequencies[key][1]}\n')
                if frequencies[key][0] == 1:
                    terms_with_freq_one += 1
            except Exception as e:
                print(e)
                print(key)
                print(frequencies[key])

def save_collection_stats():
    with open("output_02/estadisticas.txt", "w") as f:
        f.write(f'{total_docs}\n')
        f.write(f'{total_tokens} {total_terms}\n')
        f.write(f'{total_tokens/total_docs} {total_terms/total_docs}\n')
        f.write(f'{total_terms_length/total_terms}\n')
        f.write(f'{tokens_in_shortest_doc} {terms_in_shortest_doc} {tokens_in_longest_doc} {terms_in_longest_doc}\n')
        f.write(f'{terms_with_freq_one}\n')

def save_top_last_10_frequencies(frequencies):
     with open("output_02/frecuencias.txt", "w") as f:
        ordered = dict(sorted(frequencies.items(), key=lambda item: item[1]))
        keys = list(ordered.keys())
        for key in keys[-10:]:
            f.write(f"{key} {ordered[key][0]}\n")        
        for key in keys[:10]:
            f.write(f"{key} {ordered[key][0]}\n")
        #f.write(f'{total_tokens} {total_terms}\n')
        

def read_palabras_vacias(path):
    output = []
    with open(path, "r") as f: 
        for line in f.readlines():
            stop_words = line.split(",")
            output.append(stop_words)
    return [item for sublist in output for item in sublist]

def print_lists():
    print("Abreviaturas: ")
    print(abbreviations_list)
    print("\n Direcciones de correo y URLs: ")
    print(mails_urls_list)
    print("\n N??meros:")
    print(numbers_list)
    print("\n Nombres propios: ")
    print(proper_names_list)

def save_list_to_file(file, list):
    with open(f"output_02/{file}", "w", encoding="utf-8") as f:
        for entry in list:
            try:
                f.write(f"\"{entry}\",")            
            except Exception as e:
                print(e)
                print(entry)

def save_lists():
    save_list_to_file("abreviaturas.csv", abbreviations_list)
    save_list_to_file("mails_urls.csv", mails_urls_list)
    save_list_to_file("numbers.csv", numbers_list)
    save_list_to_file("proper_names.csv", proper_names_list)

# -------------------------------------

if __name__ == '__main__':
    start = time.time()
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    dirpath = sys.argv[1]
    if len(sys.argv) == 3:        
        deep_abbrv_process = sys.argv[2].lower() == "true"        
    if len(sys.argv) == 4:        
        palabras_vacias = read_palabras_vacias(sys.argv[3])
        print(palabras_vacias)
    if not os.path.exists("./output_02"):
        os.mkdir("./output_02")    
    process_dir(dirpath)
    end = time.time()
    print("\r\nExecution time: {} seconds.".format(end - start))