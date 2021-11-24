"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class PorterStemmer uses SnowballStemmer in a dictionary of documents' tokens, returning the stemmed tokens
"""


from nltk.stem.snowball import SnowballStemmer


class PorterStemmer:
    def __init__(self):
        self.snow_stemmer = SnowballStemmer(language='english')
        self.stem_words = dict()

    def stem(self, tokens_list, option="snowball"):
        if option:
            self.stem_words = [self.snow_stemmer.stem(word) for word in tokens_list]
        else:
            self.stem_words = tokens_list

        return self.stem_words