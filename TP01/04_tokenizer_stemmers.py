import sys
import pathlib
import os
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import re
import time


palabras_vacias = [] # algunas palabras a ignorar

MIN_LENGTH = 2
MAX_LENGTH = 25

total_docs = 0
total_tokens = 0
total_terms = 0

stemmer = PorterStemmer()

# -------------------------------------------
def process_dir(filepath):
    count_frequencies(filepath)    

def count_frequencies(dirpath):

    global total_docs
    global total_tokens
    global total_terms
    
    # "casa": [collection_freq, doc_freq]
    frequencies = {}    
    corpus_path = pathlib.Path(dirpath)

    for in_file in corpus_path.iterdir():
        total_docs += 1
        with open(in_file, "r", encoding="utf-8") as f:
            
            for line in f.readlines():
              
                tokens_list = [remove_punctuation(normalize(x)) for x in line.strip().split()]

                for token in tokens_list:                                      
                    total_tokens     += 1
                    if token not in palabras_vacias and len(token) >= MIN_LENGTH and len(token) <= MAX_LENGTH:
                        token = stemmer.stem(token)
                        if token in frequencies.keys():
                            frequencies[token] += 1
                        else: # Si es la primera vez que veo este token, se agrega a los términos
                            frequencies[token] = 1 
                            total_terms += 1
    return frequencies


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

def read_palabras_vacias(path):
    output = []
    with open(path, "r") as f: 
        for line in f.readlines():
            stop_words = line.split(",")
            output.append(stop_words)
    return [item for sublist in output for item in sublist]

# -------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print('Usage: 04_tokenizer_stemmers <path> <stemmer> [stop_words_path]. Es necesario pasar como argumento un path a un directorio y el tipo de stemmer: lancaster o porter')
        sys.exit(0)
    dirpath = sys.argv[1]
    stemmer_name = sys.argv[2]
    if (stemmer_name.lower() not in ["porter", "lancaster"]):
        print("Stemmer no admitido. Solo 'porter' y 'lancaster'")
    else:
        stemmer = PorterStemmer() if stemmer_name.lower() == "porter" else LancasterStemmer()
    if len(sys.argv) == 4:
        palabras_vacias = read_palabras_vacias(sys.argv[3])
        print(palabras_vacias)    

    start = time.time()        
    process_dir(dirpath)
    end = time.time()
    print(f"Total tokens: {total_tokens}")
    print(f"Total terms: {total_terms}")
    print("\r\nExecution time: {} seconds.".format(end - start))


