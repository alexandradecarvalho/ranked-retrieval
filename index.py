"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Index
"""

import psutil
import os
import heapq
import resource
import math

from tokenizer import Tokenizer
from porter_stemmer import PorterStemmer

# TODO : store in file metadata the processing done (spimi)
# TODO : explore way to access merge file straight away 

class Index:

    def __init__(self, out_file, ranking, k=1.2, b=0.75):
        self.dictionary = dict()
        self.npostings=0
        self.i = 0
        self.doc_id = 0
        self.out_file=out_file
        self.ranking = ranking
        self.docs_lenght= dict()
        self.tokenizer = Tokenizer()
        self.stemmer = PorterStemmer()
        self.k=k
        self.b=b

    def term_weight(self, postings_list):
        if self.ranking=='bm25': #bm25 formula ((k + 1) tf) / k((1-b) + b (dl / avdl)) + tfi 
            return dict(map(lambda x: (x[0],round(((self.k+1)*x[1])/ (self.k*((1-self.b)+ (self.b * (self.docs_lenght[int(x[0])]/(self.npostings/self.doc_id)))) + x[1]),2)),postings_list.items())) 
        elif self.ranking[0] == 'l':
            return dict(map(lambda x: (x[0],round((1 + math.log(x[1]))*self.doc_frequency(postings_list),2)),postings_list.items()))
        elif self.ranking[0] == 'a':
            return dict(map(lambda x: (x[0],round((0.5 + (0.5*float(x[1]) / max(postings_list.values())))*self.doc_frequency(postings_list),2)),postings_list.items()))
        elif self.ranking[0] == 'b':
            return dict(map(lambda x: (x[0],self.doc_frequency(postings_list)),postings_list.items()))
        elif self.ranking[0] == 'L':
            return dict(map(lambda x: (x[0],round(((1 + math.log(x[1])) / (1 + math.avg(postings_list.values()))*self.doc_frequency(postings_list)),2)),postings_list.items())) 

    def doc_frequency(self,postings_list):
        if self.ranking[1] == 'n':
            return 1
        elif self.ranking[1] == 't' or self.ranking=="bm25":
            return round(math.log(self.doc_id / len(postings_list)),2)
        elif self.ranking[1] == 'p':
            return round(max(0, math.log(self.doc_id-len(postings_list)/len(postings_list))),2)
 
    def merge_files(self, final_file,i, init=0):
        
        # write all lines from all temporary segments in order to temp file
        with open("temp"+self.out_file, 'w+') as output_file:
            open_files = [open((str(n) + ".").join(self.out_file.split('.'))) for n in range(init,i+1)]
            output_file.writelines(heapq.merge(*open_files))
            [f.close() for f in open_files]

        [os.remove((str(n) + ".").join(self.out_file.split('.'))) for n in range(init,i+1)]

        # write to final output file the temporary file merge result
        with open("temp"+self.out_file, 'r') as temp_file, open(final_file,'w') as output_file:
            term = ""
            postings_list = dict()
            for line in temp_file:
                contents = line.split()
                if term:
                    if contents[0] == term:
                        term_content= contents[1:]
                        for term_i in term_content:
                            term_i=term_i.split(":")
                            term_info[term_i[0]]= term_info.get(term_i[0],0)+ int(term_i[1].replace(",",""))
                    else:
                        output_file.writelines(str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                        output_file.writelines("\n")
                        term = contents[0]
                        term_info= contents[1:]
                        term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info}
                        output_file.write(contents[0] + " ")
                else:
                    term = contents[0]
                    term_info= contents[1:]
                    term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info}
                    output_file.write(contents[0] + " ")
            if term:
                output_file.writelines(str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                output_file.writelines("\n")

        os.remove("temp"+self.out_file)

    def merge_and_compute_weights(self,i, init=0):
        
        # write all lines from all temporary segments in order to temp file
        with open("temp"+self.out_file, 'w+') as output_file:
            open_files = [open((str(n) + ".").join(self.out_file.split('.'))) for n in range(init,i+1)]
            output_file.writelines(heapq.merge(*open_files))
            [f.close() for f in open_files]

        [os.remove((str(n) + ".").join(self.out_file.split('.'))) for n in range(init,i+1)]

        # write to final output file the temporary file merge result
        dict_file = open("dictionary.txt","w")
        with open("temp"+self.out_file, 'r') as temp_file, open(self.out_file,'w') as output_file:
            term = ""
            postings_list = dict()
            for line in temp_file:
                contents = line.split()
                if term:
                    if contents[0] == term:
                        term_content= contents[1:] # [docId:freq,docId:freq]
                        for term_i in term_content:  # for (doc:freq) in this term
                            term_i=term_i.split(":") #term_i = [doc,freq]
                            term_info[term_i[0]] = term_info.get(term_i[0],0)+ int(term_i[1].replace(",","")) # {postings_list[doc] += freq}
                    else:
                        term_info = self.term_weight(term_info) # postings_list[doc] is not simple frequency, but the weight (tf*df) 
                        idf = round(math.log(self.doc_id / len(term_info)),2)
                        dict_file.writelines(str(idf))
                        dict_file.writelines("\n")
                        output_file.writelines(str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                        output_file.writelines("\n")
                        term = contents[0]
                        term_info= contents[1:]
                        term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info}
                        dict_file.write(contents[0] + ":")
                else:
                    term = contents[0] # term 
                    term_info= contents[1:] # [docId:freq,docId:freq]
                    term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info} # postings_list = {docId:freq,docId:freq}
                    dict_file.write(contents[0] + ":")
            if term:
                term_info = self.term_weight(term_info)
                output_file.writelines(str(self.doc_frequency(term_info)) + ';' + str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                output_file.writelines("\n")

        os.remove("temp"+self.out_file)
        dict_file.close()

    def finalize(self):

        sep = str(self.i) + "."
        output_file=open(sep.join(self.out_file.split('.')), "w")
        
        #writing the ordered dict in the file
        for key in sorted(self.dictionary.keys()):
            output_file.write(key + " " + str(self.dictionary[key]).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":") + "\n")
        
        output_file.close()

        file_threashold= resource.getrlimit(resource.RLIMIT_NOFILE)[0]//2

        #merge segments, do it in two times if the number of segments is to high
        if self.i < file_threashold:
            self.merge_and_compute_weights( self.i)
        else:
            j=0
            for j in range((self.i//file_threashold)):
                self.merge_files((str(j) + ".").join(self.out_file.split('.')),(j+1)*(file_threashold)-1, j*(file_threashold))
            self.merge_files((str(j+1) + ".").join(self.out_file.split('.')),self.i,(j+1)*(file_threashold))
            self.merge_and_compute_weights(j+1 )

        print(f'Temporary index segments: {self.i}')

    
    def indexer(self, docs,  threshold, length, stopwords, p):

        # save indexing metadata
        os.setxattr(self.out_file, 'user.length', f'{length}'.encode())
        os.setxattr(self.out_file, 'user.stopwords', f'{stopwords}'.encode())
        os.setxattr(self.out_file, 'user.stemmer', f'{p}'.encode())
        os.setxattr(self.out_file, 'user.ranking', f'{self.ranking}'.encode())

        #tokanization and stemmig of the documents 
        documents = {key:self.stemmer.stem(self.tokenizer.tokenize(text, filter=length, option=stopwords), option=p) for key,text in docs.items()}

        idmapper = open("idmapper.txt",'w')
        for doc_id,token_list in documents.items():
            idmapper.write(doc_id+"\n")
            self.doc_id += 1
            self.docs_lenght[self.doc_id]=len(documents[doc_id]) #guardar o numero de termos para cada documento

            
            for token in token_list:
                if not token in self.dictionary: 
                    self.dictionary[token] = dict()
                self.dictionary[token][self.doc_id]=self.dictionary[token].get(self.doc_id,0)+1

                self.npostings+=1

            #saving segment to a temporary file
            if (not threshold and psutil.virtual_memory().percent >= 90) or (threshold and self.npostings >= threshold) :
                sep = str(self.i) + "."
                output_file=open(sep.join(self.out_file.split('.')), "w")
                
                #writing the ordered dict in the file
                for key in sorted(self.dictionary.keys()):
                    output_file.write(key + " " + str(self.dictionary[key]).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":") + "\n")
                
                output_file.close()
                self.dictionary=dict()
                self.npostings=0
                self.i+=1
        idmapper.close()
        return self.dictionary