"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Searcher loads the dictionary from the disk, and its search function receives a term and returns its total  frequency
"""

from tokenizer import Tokenizer 
from porter_stemmer import PorterStemmer
import math
import os

class Searcher:

    def __init__(self, index_file):
        self.dictionary = dict()
        self.stopwords = os.getxattr(index_file, 'user.stopwords').decode() if os.getxattr(index_file, 'user.stopwords').decode() != 'None' else None
        self.length = int(os.getxattr(index_file, 'user.length').decode())
        self.tokenizer = Tokenizer()
        self.stemmer=PorterStemmer() if os.getxattr(index_file, 'user.stemmer').decode()=='True' else None

        f = open(index_file, 'r')

        for line in f:
            dict_entry = line.strip().split(";")
            term, idf = dict_entry[0].split(":")
            
            d = dict()
            for items in dict_entry[1].split(","):
                k, v = items.split(":")
                d[k] = v
            
            self.dictionary[term] = (float(idf),d) # {term: (idf, {doc:tw,doc:tw})}
            
        f.close()

        self.ranking=os.getxattr(index_file, 'user.ranking').decode()

    def term_weight_query(self, query):
        tf = dict()

        for word in query:
            tf[word] = tf.get(word,0) + 1

        if self.ranking[0] == 'l':
            return dict(map(lambda x: (x[0], round(((1 + math.log(x[1])))*self.dictionary[x[0]][0],2)),tf.items()))
        elif self.ranking[0] == 'a':
            return dict(map(lambda x: (x[0],round((0.5 + (0.5* x[1] / max(tf.values())))*self.dictionary[x[0]][0],2)), tf.items()))
        elif self.ranking[0] == 'b':
            return dict(map(lambda x: (x[0], self.dictionary[x[0]][0]),tf.items()))
        elif self.ranking[0] == 'L':
            return dict(map(lambda x: (x[0], round(((1 + math.log(x[1])) / (1 + math.avg(tf.values())))*self.dictionary[x[0]][0],2)),tf.items()))

    def normalized_weights(self,weights):
        if self.ranking[2] == 'n':
            return weights
        elif self.ranking[2] == 'c':
            length = math.sqrt(sum([v**2 for v in weights.values()]))
            return dict(map(lambda x: (x[0],x[1]/length),weights.items()))
        # TODO : check other two ?

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
            twq = self.term_weight_query(inpt) # {term : tf*idf}
            normed_query_weights = self.normalized_weights(twq)

            twd = dict()
            docIds = set()
            for word in inpt:
                 docIds += set(self.dictionary[word][1].keys()) 
            
            # TODO : Find all tws for these docs in order to calculate docs lengths  
            #for doc in docIds:
            #    pass

                
            #twd[word] = dict(map(lambda x: (x[0], df*x[1]),postings_dict.items()))

        score_list= sorted(scores.items(), key=lambda x: x[1], reverse=True)[:100] #get the first 100 scores
        print("Searching query", query)
        [print(s) for s in score_list]
        # TODO: for each doc - multiply both normalized weights and add them to get doc scores