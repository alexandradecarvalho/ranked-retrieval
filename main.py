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
arg_parser.add_argument('-f','--file',nargs='?',help='File of dataset to be used')
arg_parser.add_argument('-l','--length',nargs='?',type=int, default=3,help='Length filter default is 3 if value less than 1 the filter is disabled')
arg_parser.add_argument('-s','--stopword',nargs='?', default='stopwords.txt',help='File for stopword list if no file given no stopwords will be used')
arg_parser.add_argument('-p',help='Disable porter stemmer', action='store_false')
arg_parser.add_argument('-w',nargs='?',help='Use number of postings as threashold if flag not present default is memory usage', type=int, const=100000)
arg_parser.add_argument('-d','--documents',nargs='?',type=int, default=500,help='Number of documents analysed in each iteration, by default is 500')
arg_parser.add_argument('-r','--ranking',nargs='*', default='lnc.ltc',help='')

fname_out = "out.txt"
args = arg_parser.parse_args()
ranking = args.ranking.split(" ") if type(args.ranking) != list else args.ranking

if args.file:
    parser = DocParser(args.file)    

    if ranking[0]=="bm25":
        if len(args.ranking)==1:
            index= Index(fname_out, args.ranking[0]) # Index(ranking schema, outfile)
        elif len(args.ranking)==3:
            index = Index(fname_out, args.ranking[0],float(args.ranking[1]),float(args.ranking[2])) #Index(fname_out, ranking schema, k,b)
    else:
        ranking = ranking[0].split(".")
        if  len(ranking) != 2 or len(ranking[0]) != 3 or len(ranking[1]) != 3 or ranking[0][0] not in {'n','l','a','b','L'} or ranking[1][0] not in {'n','l','a','b','L'} or ranking[0][1] not in {'n','t','p'} or ranking[1][1] not in {'n','t','p'} or ranking[0][2] not in {'n','c','u','b'} or ranking[1][2] not in {'n','c','u','b'}:
            index = Index(fname_out,'lnc.ltc')
        else:
            index = Index(fname_out,args.ranking)

    nlines = args.documents

    init_time= time.time()
    while True:
        contents=parser.read_file_csv(nlines)
        if contents:
            index.indexer(contents, args.w, args.length, args.stopword, args.p)
        else:
            break
        
    parser.close_file()
    index.finalize()

    print(f'Indexing time: {time.time()-init_time} s')
    print(f'Total index size on disk: {os.path.getsize(fname_out)/(1024*1024)} MB' )
    print(f'Vocabulary size: {sum(1 for line in open(fname_out))}')

init_time= time.time()
s = Searcher(fname_out)
print(f'Index searcher start up time: {time.time()-init_time} s')
init_time= time.time()

queries = open("queries.txt","r")
for q in queries:
    s.search(q.strip()) 
print(f'Index query search time: {time.time()-init_time} s')
