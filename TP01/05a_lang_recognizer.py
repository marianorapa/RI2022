import sys
import pathlib
import os
import numpy as np
import re
from langdetect import detect

palabras_vacias = [] # algunas palabras a ignorar

lang_detect_results = []
# -------------------------------------------

def train_models(dirpath):    
    models_path = pathlib.Path(dirpath)
    models = {}    
    for in_file in models_path.iterdir():
        models[in_file.name] = {}
        with open(in_file, "r", encoding="latin1") as f:            
            for line in f.readlines():
                line = line.lower()
                line = re.sub("[^a-z]", "", line)
            for char in line:
                if char in models[in_file.name]:
                    models[in_file.name][char] += 1
                else:
                    models[in_file.name][char] = 1     

    return models

def get_input_distributions(path):
    result = []    
    with open(path, "r", encoding="latin1") as f:
        for line in f.readlines():
            test_model = {}
            line = line.lower()
            if (len(line.strip()) > 0):
                lang_detect_results.append(detect(line))  
            line = re.sub("[^a-z]", "", line)            
            for char in line:
                if char in test_model:
                    test_model[char] += 1
                else:
                    test_model[char] = 1
            result.append(test_model)
    return result

def get_closest_model(models, inputs):
    result = []
    # Complete missing keys in each other
    for input in inputs:        
        for key in models.keys():
            for subkey in models[key]:
                if (subkey not in input):
                    input[subkey] = 0           
        for input_key in input.keys():        
            for model_key in models.keys():           
                if (input_key not in models[model_key]):
                    models[model_key][input_key] = 0            
        
        sorted_input = dict(sorted(input.items()))
        
        # Sort each model dictionary
        for key in models:
            models[key] = dict(sorted(models[key].items()))

        # Calculate Pearson correlation coef
        max_correlation = -10
        closer_model = None
        for key in models.keys():           

            for i in range(0, len(input)):
                if list(models[key].keys())[i] != list(sorted_input.keys())[i]:
                    print(f"Error. Disordered keys: {list(models[key].keys())[i]} vs {list(sorted_input.keys())[i]}")
           
            model_corr = np.corrcoef(list(models[key].values()), list(sorted_input.values()))[0,1]
           
            if (abs(model_corr) > max_correlation):                
                closer_model = key
                max_correlation = abs(model_corr)        
        result.append(closer_model)
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

def translate_lang(lang):
    if (lang == "en"): return "English"
    if (lang == "it"): return "Italian"
    if (lang == "fr"): return "French"
    return lang
    
def compare_solutions(solutions, prediction):
    match_with_solutions = 0    
    match_with_lang_detect = 0    
    match_langdetect = 0
    for i in range(0, len(solutions)):
        if (solutions[i] == prediction[i]):
            match_with_solutions += 1
        language_detected = translate_lang(lang_detect_results[i])
        if (language_detected == prediction[i]):
            match_with_lang_detect += 1 
        if (language_detected == solutions[i]):
            match_langdetect += 1
    print(f"Accuracy of program compared to solutions: {match_with_solutions/len(solutions)}")
    print(f"Accuracy of program compared to lang detect: {match_with_lang_detect/len(solutions)}")
    print(f"Accuracy of langdetect compared to solutions: {match_langdetect/len(solutions)}")

# -------------------------------------


if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print('Es necesario pasar como argumento un path a un directorio con los archivos de entrenamiento y el path a un archivo de prueba que será interpretado por linea')
        sys.exit(0)
    dirpath = sys.argv[1]
    testfilepath = sys.argv[2]    
    if not os.path.exists("./output_05"):
        os.mkdir("./output_05")    
    models = train_models(dirpath)  
    
    input_distributions = get_input_distributions(testfilepath)     
    prediction = get_closest_model(models, input_distributions)
    save_predictions(prediction)
    if (len(sys.argv)) == 4:
        solutions = load_solutions(sys.argv[3])
        compare_solutions(solutions, prediction)