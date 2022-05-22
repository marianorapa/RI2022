import sys
import time
boolean_retriever_lib = __import__("07_boolean_retriever")


def read_queries(path):
    with open(path, "r") as file:
        return file.readlines()        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un path para leer las queries")
        sys.exit(0)

    path = sys.argv[1]
    retriever = boolean_retriever_lib.BooleanRetriever()

    queries = read_queries(path)
    print(len(queries))
    start = time.time()
    for query in queries:
        retriever.process_query(query.strip(), True)
    end = time.time()
    print(f"Retrieval time with skips {end-start}")
    
    start = time.time()
    for query in queries:
        retriever.process_query(query.strip(), False)    
    end = time.time()
    print(f"Retrieval time without skips {end-start}")

    results = []
    
    