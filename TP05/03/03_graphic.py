# load matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv

def read_data(path):
    output = []
    with open(path, "r") as file:
        #lines = file.readlines()
        lines = csv.reader(file, delimiter=';')
        next(lines)
        for line in lines:   
            output.append(line)
    
    return output
##
# Barras apiladas de dinámicas y estáticas para p_logica, y otro igual para p_fisica
# #

def graph_pie_chart(data):
    dynamic = 0
    static = 0
    for page in data:
        if (str(page[4]).lower() == "true"):              
            dynamic +=1
        else:                        
            static += 1            
    y = np.array([static, dynamic])

    labels = ["Estáticas", "Dinámicas"]
    plt.figure(0)
    plt.pie(y, labels=labels)    
    plt.savefig("static-dynamic-pie.png")

def graph_logic_vs_physic(data):
    physic = {}
    logic = {}

    max_depth = 0

    for entry in data:
        l_depth = int(entry[2])
        p_depth = int(entry[3])   
        greater_depth = max(l_depth, p_depth)
        max_depth = max(greater_depth, max_depth)
        physic[p_depth] = physic[p_depth] + 1 if p_depth in physic else 1
        logic[l_depth] = logic[l_depth] + 1 if l_depth in logic else 1

    physic_series = []
    logic_series = []
    
    for i in range(0, max_depth + 1):
        physic_series.append(physic[i] if i in physic else 0)
        logic_series.append(logic[i] if i in logic else 0)
    
    plt.figure(5)
    # create plot
    fig, ax = plt.subplots()
    index = np.arange(max_depth + 1)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, physic_series, bar_width,
    alpha=opacity,
    color='b',
    label='Física')

    rects2 = plt.bar(index + bar_width, logic_series, bar_width,
    alpha=opacity,
    color='g',
    label='Lógica')    
    
    plt.xlabel('Profundidad')
    plt.ylabel('Frecuencia')
    plt.title('Frecuencia por profundidad')
    plt.xticks(index + bar_width, labels=range(0, max_depth+1))
    plt.legend()
    

    plt.tight_layout()
    plt.savefig("physic-logic-bars.png")        

def graph_dynamic_vs_static_grouped_by_depth(data):
    physic_static = {}
    physic_dynamic = {}
    logic_static = {}
    logic_dynamic = {}

    max_depth = 0

    for entry in data:
        l_depth = int(entry[2])
        p_depth = int(entry[3])   
        greater_depth = max(l_depth, p_depth)
        max_depth = max(greater_depth, max_depth)
        if (entry[4].lower() == "true"):
            physic_dynamic[p_depth] = physic_dynamic[p_depth] + 1 if p_depth in physic_dynamic else 1
            logic_dynamic[l_depth] = logic_dynamic[l_depth] + 1 if l_depth in logic_dynamic else 1
        else:
            physic_static[p_depth] = physic_static[p_depth] + 1 if p_depth in physic_static else 1
            logic_static[l_depth] = logic_static[l_depth] + 1 if l_depth in logic_static else 1

    physic_dynamic_series = []
    logic_dynamic_series = []
    
    for i in range(0, max_depth + 1):
        physic_dynamic_series.append(physic_dynamic[i] if i in physic_dynamic else 0)
        logic_dynamic_series.append(logic_dynamic[i] if i in logic_dynamic else 0)
    
    physic_static_series = []
    logic_static_series = []
    
    for i in range(0, max_depth + 1):
        physic_static_series.append(physic_static[i] if i in physic_static else 0)
        logic_static_series.append(logic_static[i] if i in logic_static else 0)

    # Logic depth static vs dynamic
    x = range(0, max_depth + 1)
    plt.figure(10)

    # plot stacked bar chart 
    plt.bar(x, logic_static_series, color='g', label="Estática")
    plt.bar(x, logic_dynamic_series, bottom=logic_static_series, color='y', label="Dinámica")

    plt.xlabel('Profundidad')
    plt.ylabel('Frecuencia')
    plt.title('Frecuencia por profundidad lógica')    
    plt.legend()    
    plt.tight_layout()
    plt.savefig("dynamic-vs-static-logic-depth.png")
    
    # Physical depth static vs dynamic
    x = range(0, max_depth + 1)
    plt.figure(15)
    # plot stacked bar chart 
    plt.bar(x, physic_static_series, color='g', label="Estática")
    plt.bar(x, physic_dynamic_series, bottom=physic_static_series, color='y', label="Dinámica")

    plt.xlabel('Profundidad')
    plt.ylabel('Frecuencia')
    plt.title('Frecuencia por profundidad física')    
    plt.legend()

    plt.tight_layout()
    plt.savefig("dynamic-vs-static-physic-depth.png")

if __name__ == '__main__':

    data = read_data("crawled_pages.txt")
    graph_pie_chart(data)

    graph_logic_vs_physic(data)
    graph_dynamic_vs_static_grouped_by_depth(data)
    # data set
    #x = ['A', 'B', 'C', 'D']
    #y1 = [100, 120, 110, 130]
    #y2 = [120, 125, 115, 125]

    ## plot stacked bar chart 
    #plt.bar(x, y1, color='g')
    #plt.bar(x, y2, bottom=y1, color='y')
    #plt.show()