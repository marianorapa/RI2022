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
    print(f"Evaluating {len(queries)} queries")
    skips_result = []
    start = time.time()
    for query in queries:
        skips_result.append(retriever.process_query(query.strip(), True))
    end = time.time()
    print(f"Retrieval time with skips {end-start}")

    non_skips_result = []    
    start = time.time()
    for query in queries:
        non_skips_result.append(retriever.process_query(query.strip(), False))
    end = time.time()
    print(f"Retrieval time without skips {end-start}")


    if (len(skips_result) != len(non_skips_result)):
        print("Something went wrong: dif result lengths")
    for i in range(0, len(skips_result)):
        a_skips_result = skips_result[i]
        a_non_skips_result = non_skips_result[i]
        if (len(a_skips_result) != len(a_non_skips_result)):
            print(f"Error: length of query {i} differs from each other: {a_skips_result} vs {a_non_skips_result}")
        for j in range(0, len(a_skips_result)):
            if a_skips_result[j] != a_non_skips_result[j]:
                print(f"One of the doc ids for query {i} is different in result {j}: {a_skips_result[j]} != {a_non_skips_result[j]}")   
    