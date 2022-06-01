import sys
import time
indexer_lib = __import__("11_indexer")


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Es obligatorio un path para indexar")
        sys.exit(0)

    path = sys.argv[1]
    indexer = indexer_lib.FrequencyIndexer()
    
    indexer.index_dir(path)

    start = time.time()
    indexer.save_index("11_index_variable_byte.bin", 2)        
    end = time.time()
    print(f"Variable Byte compression index saving time: {end - start}")
    #indexer.__save_vocabulary__("11_vocab_variable_byte.bin")
    start = time.time()
    indexer.load_index_with_loaded_dict("11_index_variable_byte.bin", 2)
    end = time.time()
    print(f"Variable Byte index decompression time: {end - start}")

    start = time.time()
    indexer.save_index("11_index_gamma.bin", 1)        
    end = time.time()        
    #indexer.__save_vocabulary__("11_vocab_gamma.bin")
    print(f"Gamma compression index saving time: {end - start}")
    start = time.time()
    indexer.load_index_with_loaded_dict("11_index_gamma.bin", 1)
    end = time.time()
    print(f"Gamma index decompression time: {end - start}")

    # With gaps
    start = time.time()
    indexer.save_index_with_gaps("11_index_gaps_variable_byte.bin", 2)        
    end = time.time()
    #indexer.__save_vocabulary__("11_vocab_gaps_variable_byte.bin")
    print(f"Variable Byte compression index with gaps saving time: {end - start}")     
    start = time.time()
    indexer.load_index_with_loaded_dict("11_index_gaps_variable_byte.bin", 2)
    end = time.time()
    print(f"Variable Byte index with gaps decompression time: {end - start}")

    start = time.time()
    indexer.save_index_with_gaps("11_index_gaps_gamma.bin", 1)        
    end = time.time()        
    #indexer.__save_vocabulary__("11_vocab_gaps_gamma.bin")
    print(f"Gamma compression index with gaps saving time: {end - start}")  
    start = time.time()
    indexer.load_index_with_loaded_dict("11_index_gaps_gamma.bin", 1)
    end = time.time()
    print(f"Gamma index with gaps decompression time: {end - start}")  
    
       