"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins
"""


from doc_parser import DocParser
from argparse import ArgumentParser
from tokenizer import Tokenizer
from porter_stemmer import PorterStemmer
from index import Index
from searcher import Searcher

import time
import os

arg_parser=ArgumentParser(prog='index creator')
arg_parser.add_argument('-f','--file',nargs=1,help='File of dataset to be used', required=True)
arg_parser.add_argument('-l','--length',nargs='?',type=int, default=3,help='Length filter default is 3 if value less than 1 the filter is disabled')
arg_parser.add_argument('-s','--stopword',nargs='?', default='stopwords.txt',help='File for stopword list if no file given no stopwords will be used')
arg_parser.add_argument('-p',help='Disable porter stemmer', action='store_false')
arg_parser.add_argument('-w',nargs='?',help='Use number of postings as threashold if flag not present default is memory usage', type=int, const=100000)
arg_parser.add_argument('-d','--documents',nargs='?',type=int, default=500,help='Number of documents analysed in each iteration, by default is 500')
args = arg_parser.parse_args()


#print("---PARSING DOCUMENTS--")
parser = DocParser(args.file[0])
index= Index()

fname_out = "out.txt"

nlines = args.documents

init_time= time.time()
while True:
    contents=parser.read_file_csv(nlines)
    if contents:
        index.indexer(contents, fname_out, args.w, args.length, args.stopword, args.p)
    else:
        break
    
parser.close_file()
index.finalize(fname_out)

print(f'Indexing time: {time.time()-init_time} s')
print(f'Total index size on disk: {os.path.getsize(fname_out)/(1024*1024)} MB' )
print(f'Vocabulary size: {sum(1 for line in open(fname_out))}')

init_time= time.time()
s = Searcher(fname_out,args.p)
print(f'Index searcher start up time: {time.time()-init_time} s')

s.search()
