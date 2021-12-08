"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Searcher loads the dictionary from the disk, and its search function receives a term and returns its total  frequency
"""

from os import terminal_size
from porter_stemmer import PorterStemmer
import math

class Searcher:

    def __init__(self, index_file, stemmer):
        self.dictionary = dict()
        self.stemmer=PorterStemmer() if stemmer else None

        f = open(index_file, 'r')

        for line in f:
            dict_entry = line.strip().split(";")
            term, idf = dict_entry[0].split(":")
            
            d = dict()
            for items in dict_entry[1].split(","):
                k, v = items.split(":")
                d[k] = v
            
            self.dictionary[term] = (idf,d)
            
        f.close()

    def term_weight(self, query):
        tf = dict()

        for word in query:
            tf[word] = tf.get(word,0) + 1

        if self.ranking[0] == 'l':
            return dict(map(lambda x: (x[0], round(1 + math.log(x[1]),2))),tf.items())
        elif self.ranking[0] == 'a':
            return dict(map(lambda x: (x[0],round(0.5 + (0.5* x[1] / max(tf.values())),2))))
        elif self.ranking[0] == 'b':
            return dict(map(lambda x: (x[0], 1)),tf.items())
        elif self.ranking[0] == 'L':
            return dict(map(lambda x: (x[0], round((1 + math.log(x[1])) / (1 + math.avg(tf.values())),2))),tf.items())

    def search(self,inpt):
        inpt=inpt.lower().split()

        if self.stemmer:
            inpt = self.stemmer.stem(inpt)

        tf = self.term_weight(inpt)

        weights = dict()

        for word, term_freq in tf:
            weights[word] = term_freq * self.dictionary.get(word,(0,0))[0] # w = tf * idf


        # TODO: normalizar os 2 pesos, multiplicá-los e somar as multiplicações por doc para obter o ranking dos docs