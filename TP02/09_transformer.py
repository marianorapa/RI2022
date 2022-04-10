from audioop import reverse
import sys
import pathlib
import math


####
# Reads cisi.all and transforms into TREC
# <DOC>
# <DOCNO>document number</DOCNO>
# contenido del documento
# </DOC>
####


def parse_documents(file):
    documents = {}
    with open(file, "r") as f:         
        incoming_title = False
        incoming_author = False        
        incoming_text = False
        doc_counter = 1
        title = ""
        author = ""
        text = ""
        for line in f.readlines():            
            line = line.strip()
            if incoming_title:
                title = line
                incoming_title = False
            if incoming_author:
                author = line
                incoming_author = False            
            if line == ".T":                
                incoming_title = True
            elif line == ".A":
                incoming_author = True
            elif line == ".W":
                incoming_text = True
            elif line == ".X":
                incoming_text = False
                documents[doc_counter] = [title, author, text]
                doc_counter += 1
                text = ""
            if incoming_text and line != ".W":
                text += line
            

    return documents
    
def save_documents_trec(documents):
    with open("09_cisi_trec.txt", "w") as f:
        for key in documents.keys():
            output = f"<DOC>\n<DOCNO>{key}</DOCNO>\n{documents[key][0]} - {documents[key][2]}\n</DOC>\n"
            f.write(output)

if __name__ == '__main__':
    input_file = sys.argv[1]        
    documents = parse_documents(input_file)
    save_documents_trec(documents)