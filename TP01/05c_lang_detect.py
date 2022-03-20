import sys
import os
from langdetect import detect

palabras_vacias = [] # algunas palabras a ignorar

# -------------------------------------------

def detect_languages(path):
    result = []    
    with open(path, "r", encoding="latin1") as f:
        for line in f.readlines():            
            line = line.lower()
            #line = re.sub("[^a-z]", "", line)
            result.append(detect(line))            
    return result

def save_predictions(predictions):
    with open("output_05/a_predictions.txt", "w") as f:
        for prediction in predictions:
            f.write(f"{prediction}\n")

def load_solutions(path):
    solutions = []
    with open(path, "r", encoding="latin1") as f:
        for line in f.readlines():
            solutions.append(line.split(" ")[1].replace("\n", ""))
    return solutions

def compare_solutions(solutions, prediction):
    match = 0    
    for i in range(0, len(solutions)):
        if (solutions[i] == prediction[i]):
            match += 1
    print(f"Accuracy: {match/len(solutions)}")

# -------------------------------------


if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio con el archivo de prueba que será interpretado por linea')
        sys.exit(0)
    filepath = sys.argv[1]    
    if not os.path.exists("./output_05"):
        os.mkdir("./output_05")    
    results = detect_languages(filepath)
    