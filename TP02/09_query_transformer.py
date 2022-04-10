from audioop import reverse
import sys
import pathlib
import math
import re

####
# Reads cisi.all and transforms into TREC
# <DOC>
# <DOCNO>document number</DOCNO>
# contenido del documento
# </DOC>
####


def parse_queries(file):
    queries = {}
    with open(file, "r") as f:         
        for line in f.readlines():
            line = line.strip()
            terms = re.findall('\'([a-zA-Z]+)\'', line)
            query_id = line.split("=")[0].replace("#q", "")
            if len(terms) > 0:
                queries[query_id] = terms
    return queries
    
def save_queries_trec(queries):
    with open("09_cisi_topics.txt", "w") as f:
        for key in queries.keys():
            queries_string = ""
            for term in queries[key]:
                queries_string += f"{term} "
            output = f"<TOP>\n<NUM>{key}<NUM>\n<TITLE>{queries_string.strip()}\n<DESC>\n<NARR>\n</TOP>\n"
            f.write(output)
  

if __name__ == '__main__':
    input_file = sys.argv[1]        
    queries = parse_queries(input_file)
    save_queries_trec(queries)