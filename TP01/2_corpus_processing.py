# - Recorrer todos los archivos de un directorio y contar frecuencias de palabras
# - Eliminar del análisis a aquellas palabras que pertecen al grupo de "palabras vacías"
# - Pasar a minúsculas y eliminar las tildes de las palabras procesadas
# - Crear bar chart de frecuencias

import sys
import pathlib

palabras_vacias = ['alla','de','despues','no','por'] # algunas palabras a ignorar

MIN_LENGTH = 2
MAX_LENGTH = 50

## [doc_name, total_tokens, total_terms, total_terms_length]
TOTAL_TOKENS_POS        = 1
TOTAL_TERMS_POS         = 2
TOTAL_TERMS_LENGTH_POS  = 3
collection_stats = []

total_docs = 0
total_tokens = 0
total_terms = 0
total_terms_length = 0
tokens_in_shortest_doc = 10000
terms_in_shortest_doc = 10000
tokens_in_longest_doc = 0
terms_in_longest_doc = 0
terms_with_freq_one = 0


# -------------------------------------------
def process_dir(filepath):
    frequencies = count_frequencies(filepath)
    save_frequencies(frequencies)
    save_collection_stats(collection_stats)

def count_frequencies(dirpath):
    # "casa": [collection_freq, doc_freq]
    frequencies = {}    
    corpus_path = pathlib.Path(dirpath)
    for in_file in corpus_path.iterdir():
        total_docs += 1
        document_stats = [in_file.name, 0, 0, 0]            # Se inicializa nueva entrada para las collection_stats
        document_terms = []
        with open(in_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                tokens_list =  filter(lambda x: x not in palabras_vacias and len(x) >= MIN_LENGTH and len(x) <= MAX_LENGTH,
                                     [normalize(x) for x in line.strip().split()])                                
                for token in tokens_list:
                    document_stats[TOTAL_TOKENS_POS] += 1
                    total_tokens += 1
                    if token in frequencies.keys():
                        frequencies[token] = [frequencies[token][0] + 1, frequencies[token][1]]                        
                    else:
                        frequencies[token] = [1, 0]         ## doc_freq se inicializa en 0 porque a continuación se incrementa
                        total_terms += 1
                        total_terms_length += len(token)
                    if token not in document_terms:
                        document_stats[TOTAL_TERMS_POS] += 1
                        document_terms.append(token)
                        document_stats[TOTAL_TERMS_LENGTH_POS] += len(token)
                        frequencies[token] = [frequencies[token][0], frequencies[token][1] + 1]                
            collection_stats.append(document_stats)
            total_doc_tokens = document_stats[TOTAL_TOKENS_POS]
            if (total_doc_tokens < tokens_in_shortest_doc):
                tokens_in_shortest_doc = total_doc_tokens
                terms_in_shortest_doc = document_stats[TOTAL_TERMS_POS]
            elif (total_doc_tokens > tokens_in_longest_doc):
                tokens_in_longest_doc = total_doc_tokens
                terms_in_longest_doc = document_stats[TOTAL_TERMS_POS]   
    return frequencies


def translate(to_translate):
	tabin = u'áéíóú'
	tabout = u'aeiou'
	tabin = [ord(char) for char in tabin]
	translate_table = dict(zip(tabin, tabout))
	return to_translate.translate(translate_table)


def normalize(token):
    result = token.lower()
    result = translate(result)   
    return result

def save_frequencies(frequencies):
	# guardar en un archivo frecuencias ordenadas por valor
    with open("terminos.txt", "w") as f:
        for key in sorted(frequencies):
            f.write(f'{key} {frequencies[key][0]} {frequencies[key][1]}\n')
            if frequencies[key][0] == 1:
                terms_with_freq_one += 1

def save_collection_stats(collection_stats): 
    total_processed_docs = len(collection_stats)
    
    with open("estadisticas.txt", "w") as f:
        f.write(f'{total_processed_docs}')
        f.write(f'{total_tokens} {total_terms}')
        f.write(f'{total_tokens/total_processed_docs} {total_terms/total_processed_docs}')
        f.write(f'{total_terms_length/total_processed_docs}')
        f.write(f'{tokens_in_shortest_doc} {terms_in_shortest_doc} {tokens_in_longest_doc} {terms_in_longest_doc}')
        f.write(f'{terms_with_freq_one}')


        

def read_palabras_vacias(path):
    output = []
    with open(path, "r") as f: 
        for line in f.readlines():
            stop_words = line.split(",")
            output.append(stop_words)
    return output
# -------------------------------------

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    dirpath = sys.argv[1]
    if len(sys.argv) == 3:
        palabras_vacias = read_palabras_vacias(sys.argv[2])
    process_dir(dirpath)



