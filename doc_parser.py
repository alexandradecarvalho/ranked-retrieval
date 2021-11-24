"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class DocParser opens a tsv file and reads it returning a dictionary 
with review_id as key and review_headline, review_body and product title as values 
"""


import csv  

class DocParser:

    def __init__(self, filename):
        self.file=open(filename, "r")
        self.reader=csv.DictReader(self.file, delimiter="\t", quoting=csv.QUOTE_NONE)
    
    def read_file_csv(self, nlines):
        doc_contents=dict()

        for doc in range(nlines):
            try:
                row = self.reader.__next__()
            except StopIteration:
                if doc == 0:
                    return None
            
            doc_contents[row['review_id']] = row['product_title'] + ' ' + row['review_headline'] + ' ' + row['review_body']
        
        return doc_contents

    def close_file(self):
        self.file.close()
