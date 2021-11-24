"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Tokenizer tokenizes each document of a given corpus, filtering small words, stopwords, 
spaces and punctuation and returns a list of tokens
"""


import re


class Tokenizer:

    def __init__(self):
        self.stopwords = {}
        self.token_lists = []

    def tokenize(self, doc, filter = 3, option = ""):

        ##### CREATING STOPWORDS LIST #####
        if not option:
            self.stopwords = set()
        else:
            try:
                f = open(option,'r')
                self.stopwords = f.readlines()
                f.close()
            except:
                self.stopwords = set()
        
        ##### FILTERING SMALL WORDS #####
        if not filter:
            length_threshold = 0
        else:
            length_threshold = int(filter)

        ##### SPLITTING BY SPACES AND PUNCTUATION #####
        text_tokens = re.split('\W+', doc) 
        self.token_lists = [word.lower() for word in text_tokens if len(word) > length_threshold and not word.isnumeric() and not word in self.stopwords]

        return self.token_lists

