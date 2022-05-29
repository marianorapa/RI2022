import sys
import time
boolean_retriever_lib = __import__("07_boolean_retriever")

def read_queries(path):
    with open(path, "r") as file:
        return file.readlines()        

def print_stats(stats):
    with open("07_retrieval_stats.csv", "w") as file:
        file.write("query_length;terms_postings_length;skips_retrieval_time;non_skips_retrieval_time\n")
        for stat in stats:
            skips_retrieval_time = stat[2]
            non_skips_retrieval_time = stat[3]
            skips_retrieval_time_formatted = str(skips_retrieval_time).replace(".", ",")
            non_skips_retrieval_time_formatted = str(non_skips_retrieval_time).replace(".", ",")
            output = f"{stat[0]};{stat[1]};{skips_retrieval_time_formatted};{non_skips_retrieval_time_formatted}\n"
            file.write(output)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Es obligatorio un path para leer las queries")
        sys.exit(0)

    path = sys.argv[1]
    retriever = boolean_retriever_lib.BooleanRetriever()

    queries = read_queries(path)
    print(f"Evaluating {len(queries)} queries")
        
    retrieval_stats = []
    
    skips_result = []
    non_skips_result = []    

    #start = time.time()
    for query in queries:       
        
        query_start = time.time()
        results, posting_lengths, query_len = retriever.process_query(query.strip(), True)
        query_end = time.time()
        
        skips_time = query_end - query_start
        skips_result.append(results)
        
        query_start = time.time()
        results, posting_lengths, query_len = retriever.process_query(query.strip(), False)
        query_end = time.time()
        non_skips_result.append(results)
        non_skips_time = query_end - query_start

        retrieval_stats.append([query_len, posting_lengths, skips_time, non_skips_time])
    #end = time.time()
    #print(f"Retrieval time with skips {end-start}")

    
    #start = time.time()
    #for query in queries:
    #    query_length = len(query)
    #    query_start = time.time()
    #    results, posting_lengths = retriever.process_query(query.strip(), False)
    #    query_end = time.time()
    #    non_skips_result.append(results)
    #    retrieval_stats.append([False, query_length, posting_lengths, query_end - query_start])
    #end = time.time()
    #print(f"Retrieval time without skips {end-start}")


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
    

    print_stats(retrieval_stats)