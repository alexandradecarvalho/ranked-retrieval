"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Searcher loads the dictionary from the disk, and its search function receives a term and returns its total  frequency
"""

from tokenizer import Tokenizer 
from porter_stemmer import PorterStemmer
import math
import os
import linecache


class Searcher:

    def __init__(self, index_file):
        self.index_file = index_file
        self.dictionary = dict()
        self.stopwords = os.getxattr(index_file, 'user.stopwords').decode() if os.getxattr(index_file, 'user.stopwords').decode() != 'None' else None
        self.length = int(os.getxattr(index_file, 'user.length').decode())
        self.tokenizer = Tokenizer()
        self.stemmer=PorterStemmer() if os.getxattr(index_file, 'user.stemmer').decode()=='True' else None

        f = open("dictionary.txt", 'r')
        counter = 0
        for line in f:
            counter += 1
            term, idf = line.strip().split(":")
            
            self.dictionary[term] = (float(idf),counter)  # TODO: Maybe change this to tree            
        f.close()

        self.ranking=os.getxattr(index_file, 'user.ranking').decode()

    def term_weight_query(self, query):
        tf = dict()

        for word in query:
            tf[word] = tf.get(word,0) + 1

        if self.ranking[4] == 'l':
            return dict(map(lambda x: (x[0], round(((1 + math.log(x[1])))*self.dictionary[x[0]][0],2)),tf.items()))
        elif self.ranking[4] == 'a':
            return dict(map(lambda x: (x[0],round((0.5 + (0.5* x[1] / max(tf.values())))*self.dictionary[x[0]][0],2)), tf.items()))
        elif self.ranking[4] == 'b':
            return dict(map(lambda x: (x[0], self.dictionary[x[0]][0]),tf.items()))
        elif self.ranking[4] == 'L':
            return dict(map(lambda x: (x[0], round(((1 + math.log(x[1])) / (1 + math.avg(tf.values())))*self.dictionary[x[0]][0],2)),tf.items()))
        else:
            return tf

    def normalized_query_weights(self,weights):
        if self.ranking[6] == 'c':
            length = math.sqrt(sum([v**2 for v in weights.values()]))
            return dict(map(lambda x: (x[0],x[1]/length),weights.items()))
        else:
            return weights

    def search(self,query):
        inpt=query.lower()
        scores=dict()

        inpt = self.tokenizer.tokenize(inpt, filter=self.length, option=self.stopwords)

        if self.stemmer:
            inpt = self.stemmer.stem(inpt)

        inpt = [term for term in inpt if term in self.dictionary]

        if self.ranking.split(" ")[0] == "bm25":
            for word in inpt:
                for item in linecache.getline(self.index_file, self.dictionary[word][1]).split(","): # doc:tw,doc:tw
                    tup = item.split(":")
                    scores[tup[0]] =  scores.get(tup[0],0) + self.dictionary[word][0] * float(tup[1])
        else:
            twq = self.normalized_query_weights(self.term_weight_query(inpt)) # {term : norm_w}
            for word in inpt:
                for item in linecache.getline(self.index_file, self.dictionary[word][1]).split(","):
                    tup = item.split(":")
                    scores[tup[0]] = scores.get(tup[0],0) + (twq[word]*float(tup[1])) 
            
        score_list= sorted(scores.items(), key=lambda x: x[1], reverse=True)[:100] #get the first 100 scores
        print("\nQ:", query)
        [print(linecache.getline("idmapper.txt",int(s[0])).strip().replace("\n","")) for s in score_list]