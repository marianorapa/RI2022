from re import sub
import sys
import time
boolean_retriever_lib = __import__("02_boolean_retriever")


def read_queries(path):
    with open(path, "r") as file:
        return file.readlines()        

def transform_query_multiple(query):
    parts = query.split(" ")
    if len(parts) == 2:
        or_op = f"{parts[0]} | {parts[1]}"
        and_op = f"{parts[0]} & {parts[1]}"
        neg_op = f"{parts[0]} - {parts[1]}"
        return [or_op, and_op, neg_op]
    if len(parts) == 3:
        q1 = f"{parts[0]} & {parts[1]} & {parts[2]}"
        q2 = f"({parts[0]} | {parts[1]}) - {parts[2]}"
        q3 = f"({parts[0]} - {parts[1]}) | {parts[2]}"
        return [q1, q2, q3]

def transform_query_simple(query):
    parts = query.split(" ")
    if len(parts) == 2:
        and_op = f"{parts[0]} & {parts[1]}"
        return and_op
    if len(parts) == 3:
        q1 = f"{parts[0]} & {parts[1]} & {parts[2]}"
        return q1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un path para leer las queries")
        sys.exit(0)

    path = sys.argv[1]
    retriever = boolean_retriever_lib.BooleanRetriever()

    queries = []
    initial_queries = read_queries(path)
    for query in initial_queries:
        queries.append(transform_query_simple(query))
    start = time.time()
    
    for query in queries:
        retriever.process_query(query.strip(), True)
    end = time.time()
    print(f"Retrieval time with set operations {end-start}")
    
    start = time.time()
    for query in queries:
        retriever.process_query(query.strip(), False)   
    end = time.time()
    print(f"Retrieval time with TAAT {end-start}")

    results = []   