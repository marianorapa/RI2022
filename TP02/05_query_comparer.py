from audioop import reverse
import sys
import pathlib
import math


def parse_results(file):
    results = {}
    with open(file, "r") as f:                 
        for line in f.readlines():            
            line = line.strip()
            parts = line.split(" ")
            query_id = parts[0]
            doc_id = parts[2]
            if (query_id not in results):
                results[query_id] = {}
            results[query_id][doc_id] = int(parts[3])
    return results
    
def augment_results(results_1, results_2):    
    for key in results_1.keys():
        if key not in results_2:
            results_2[key] = results_2[list(results_2.keys())[-1]] + 1
    for key in results_2.keys():
        if key not in results_1:
            results_1[key] = results_1[list(results_1.keys())[-1]] + 1

def save_documents_trec(documents):
    with open("09_cisi_trec.txt", "w") as f:        
            f.write(output)

def spearman_coef(ranking_1, ranking_2):
    sum = 0
    for key in ranking_1.keys():
        pos_1 = ranking_1[key]
        pos_2 = ranking_2[key]
        squared_dif = pow(pos_1-pos_2, 2)
        sum += squared_dif
    k = len(ranking_1.keys())    
    return 1 - (6*sum) / (k * (pow(k,2) - 1))


if __name__ == '__main__':
    file_results_1 = sys.argv[1]
    file_results_2 = sys.argv[2]
    
    results_1 = parse_results(file_results_1)
    results_2 = parse_results(file_results_2)
    
    for query in results_1.keys():
        augment_results(results_1[query], results_2[query])

    coefs = []
    for query in results_1.keys():        
        coef = spearman_coef(results_1[query], results_2[query])
        coefs.append(coef)
    
    print(coefs)    