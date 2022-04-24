import sys

from indexer import Indexer
from retriever import Retriever

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Es necesario pasar como argumento un path a un directorio')
        sys.exit(0)
    
    dir = sys.argv[1]

    indexer = Indexer()
    index = indexer.index_dir(dir)

    retriever = Retriever(indexer)
    
    while True:
        query = input("Ingresar query: ")
        results = retriever.retrieve_docs(query)
        print(results)