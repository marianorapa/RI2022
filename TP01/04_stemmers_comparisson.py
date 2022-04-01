import sys
import pathlib
import os
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import re

palabras_vacias = [] # algunas palabras a ignorar

MIN_LENGTH = 3
MAX_LENGTH = 25

total_docs = 0
total_tokens = 0
total_terms = 0


OUTPUT_DIR = "./output_04"

# -------------------------------------------
def process_dir(filepath):
    result = compare_stemmers(filepath)
    save_comparisson(result)

def compare_stemmers(dirpath):
    
    porter_stemmer = PorterStemmer()
    lancaster_stemmer = LancasterStemmer()

    global total_docs
    global total_tokens
    global total_terms
        
    # "casa": [collection_freq, doc_freq]
    output = {}    
    corpus_path = pathlib.Path(dirpath)

    for in_file in corpus_path.iterdir():
        total_docs += 1
        with open(in_file, "r", encoding="utf-8") as f:
            
            for line in f.readlines():
              
                tokens_list = [remove_punctuation(normalize(x)) for x in line.strip().split()]

                for token in tokens_list:                                      
                    total_tokens     += 1
                    if token not in palabras_vacias and len(token) >= MIN_LENGTH and len(token) <= MAX_LENGTH:
                        by_porter = porter_stemmer.stem(token)
                        by_lancaster = lancaster_stemmer.stem(token)
                        if (token) not in output:
                            output[token] = [by_porter, by_lancaster]
    return output


def translate(to_translate):
	tabin = u'áäâàãéëèêẽíïĩìîóõöòôúüùûũ'
	tabout = u'aaaaaeeeeeiiiiiooooouuuuu'
	tabin = [ord(char) for char in tabin]
	translate_table = dict(zip(tabin, tabout))
	return to_translate.translate(translate_table)

def remove_punctuation(token):
    return re.sub("[\W_]", "", token)

def normalize(token):
    result = token.lower()
    result = translate(result)           
    return result

def save_comparisson(comparisson):
    with open(f"{OUTPUT_DIR}/comparisson.txt", "w", encoding="utf-8") as f:
        for key in sorted(comparisson):
            try:
                f.write(f'{key} {comparisson[key][0]} {comparisson[key][1]}\n')
            except Exception as e:
                print(e)
                print(key)
                print(comparisson[key])

def read_palabras_vacias(path):
    output = []
    with open(path, "r") as f: 
        for line in f.readlines():
            stop_words = line.split(",")
            output.append(stop_words)
    return [item for sublist in output for item in sublist]

# -------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio y el tipo de stemmer: lancaster o porter')
        sys.exit(0)
    dirpath = sys.argv[1]
    if len(sys.argv) == 3:
        palabras_vacias = read_palabras_vacias(sys.argv[2])
        print(palabras_vacias)    
  
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)    
    process_dir(dirpath)
