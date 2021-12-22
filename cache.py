"""
Information Retrieval Assignment 2 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Cache stores postings lists for a number terms
"""


class Cache:

    def __init__(self, cachesize = 5000):
        self.postingslists = {}
        self.recorded_terms = []

    def add(self, term, postings_list):
        if term not in postings_list:
            if len(self.postingslists) == 5000:
                deleting_term = self.recorded_terms.pop(0)
                del self.postingslists[deleting_term]
            self.postingslists[term] = postings_list
        else:
            self.recorded_terms.remove(term)
            
        self.recorded_terms += [term]

    def is_cached(self,word):
        return word in self.recorded_terms

    def get(self,word):
        return self.postingslists[word]