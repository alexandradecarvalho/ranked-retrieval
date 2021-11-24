"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Searcher loads the dictionary from the disk, and its search function receives a term and returns its total  frequency
"""

from porter_stemmer import PorterStemmer

class Searcher:

    def __init__(self, index_file, stemmer):
        self.frequencies = dict()
        self.stemmer=PorterStemmer() if stemmer else None

        f = open(index_file, 'r')

        for line in f:
            dict_entry = line.strip().split()
            self.frequencies[dict_entry[0]] = len(dict_entry[1:])
    
        f.close()

    def search(self):
        while True:
            inpt = input("search: ")
            if not inpt:
                break

            inpt=inpt.lower()

            if self.stemmer:
                inpt= self.stemmer.stem([inpt])[0]

            if inpt in self.frequencies:
                print(self.frequencies[inpt])
            else:
                print(0)