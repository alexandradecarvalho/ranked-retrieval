"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Searcher loads the dictionary from the disk, and its search function receives a term and returns its total  frequency
"""

from tokenizer import Tokenizer 
from porter_stemmer import PorterStemmer
import math

class Searcher:

    def __init__(self, index_file, stemmer, ranking, stopwords, length):
        self.dictionary = dict()
        self.stopwords = stopwords
        self.length = length
        self.tokenizer = Tokenizer()
        self.stemmer=PorterStemmer() if stemmer else None

        f = open(index_file, 'r')

        for line in f:
            dict_entry = line.strip().split(";")
            term, idf = dict_entry[0].split(":")
            
            d = dict()
            for items in dict_entry[1].split(","):
                k, v = items.split(":")
                d[k] = v
            
            self.dictionary[term] = (float(idf),d)
            
        f.close()

        self.ranking=ranking

    def term_weight(self, query):
        tf = dict()

        for word in query:
            tf[word] = tf.get(word,0) + 1

        if self.ranking[0] == 'l':
            return dict(map(lambda x: (x[0], round(1 + math.log(x[1]),2)),tf.items()))
        elif self.ranking[0] == 'a':
            return dict(map(lambda x: (x[0],round(0.5 + (0.5* x[1] / max(tf.values())),2)), tf.items()))
        elif self.ranking[0] == 'b':
            return dict(map(lambda x: (x[0], 1),tf.items()))
        elif self.ranking[0] == 'L':
            return dict(map(lambda x: (x[0], round((1 + math.log(x[1])) / (1 + math.avg(tf.values())),2)),tf.items()))

    def search(self,query):
        inpt=query.lower()
        scores=dict()

        inpt = self.tokenizer.tokenize(inpt, filter=self.length, option=self.stopwords)

        if self.stemmer:
            inpt = self.stemmer.stem(inpt)

        if self.ranking=="bm25":
            for word in inpt:
                if word in self.dictionary:
                    for dic in self.dictionary[word][1]:
                        scores[dic] =  scores.get(dic,0) + self.dictionary[word][0] * float(self.dictionary[word][1][dic])
        else:
            tf = self.term_weight(inpt)
            for word in inpt:
                self.dict[word]
            query_weights = dict()
            for word, term_freq in tf.items():
                query_weights[word] = term_freq * self.dictionary.get(word,(0,0))[0] # w = tf * idf


        score_list= sorted(scores.items(), key=lambda x: x[1], reverse=True)[:100] #get the first 100 scores
        print("Searching query", query)
        [print(s) for s in score_list]
        # TODO: normalizar os 2 pesos, multiplicá-los e somar as multiplicações por doc para obter o ranking dos docs