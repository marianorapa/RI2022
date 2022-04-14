from audioop import reverse
import sys
import pathlib
import math


def read_results(file):
    results = []
    with open(file, "r") as f:         
        return f.readlines()        

def read_equivalences(file):
    equivalences = {}
    with open(file, "r") as f:         
        lines = f.readlines()
        for line in lines:
            doc_id = line.split(",")[0].strip()
            doc_name = line.split("/")[-1].strip()
            equivalences[doc_name] = doc_id
    return equivalences

def transform_results(results, equivalences):
    transformed = []
    for result in results:
        entry_parts = result.split(" ")
        entry_parts[2] = equivalences[entry_parts[2]]        
        transformed_result = f"{entry_parts[0]} {entry_parts[1]} {entry_parts[2]} {entry_parts[3]} {entry_parts[4]}"
        transformed.append(transformed_result)
    
    return transformed

def save_results(results):
    path = "07_transformed_results.txt"
    with open(path, "w", encoding="utf-8") as f:
        for result in results:            
            f.write(result)


if __name__ == '__main__':
    input_file = sys.argv[1]        
    equivalences_file = sys.argv[2]
    
    results = read_results(input_file)
    equivalences = read_equivalences(equivalences_file)    
    transformed = transform_results(results, equivalences)    
    save_results(transformed)
