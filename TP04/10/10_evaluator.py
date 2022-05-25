import sys
import time
boolean_retriever_lib = __import__("10_boolean_retriever")


def read_queries(path):
    with open(path, "r") as file:
        return file.readlines()

def save_stats_to_file(path, stats):
    with open(path, "w") as file:
        for stat in stats.keys():
            file.write(f"{stat};{stats[stat][0]};{stats[stat][1]};{stats[stat][2]}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un path para leer las queries")
        sys.exit(0)

    path = sys.argv[1]
    retriever = boolean_retriever_lib.BooleanRetriever()

    queries = read_queries(path)
    print(f"Evaluating {len(queries)} queries")
    

    taat_times = {}
    i = 0
    for query in queries:
        start = time.time()
        result, postings_length = retriever.process_query(query.strip(), True)
        end = time.time()
        taat_times[i] = [len(query), postings_length, end-start]
        i += 1

    daat_times = {}
    i = 0        
    for query in queries:
        start = time.time()
        result, postings_length = retriever.process_query(query.strip(), False)
        end = time.time()
        daat_times[i] = [len(query), postings_length, end-start]
        i += 1

    save_stats_to_file("./taat_times.csv", taat_times)
    save_stats_to_file("./daat_times.csv", daat_times)
       