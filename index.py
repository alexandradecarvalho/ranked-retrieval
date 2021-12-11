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

class Index:

    def __init__(self, ranking, bm25, k=1.2, b=0.75):
        self.dictionary = dict()
        self.npostings=0
        self.i = 0
        self.doc_id = 0
        self.ranking = ranking
        self.docs_lenght= dict()
        self.tokenizer = Tokenizer()
        self.stemmer = PorterStemmer()
        self.bm25=bm25
        self.k=k
        self.b=b


    def term_weight(self, postings_list):
        if self.ranking=='bm25': #bm25 formula ((k + 1) tf) / k((1-b) + b (dl / avdl)) + tfi
            for doc in postings_list:
                postings_list[doc] = round(((self.k+1)*postings_list[doc])/ (self.k*((1-self.b)+ (self.b * (self.docs_lenght[int(doc)]/(self.npostings/self.doc_id)))) + postings_list[doc]),2)
        elif self.ranking[0] == 'l':
            for doc in postings_list:
                postings_list[doc] = round(1 + math.log(postings_list[doc]),2)
        elif self.ranking[0] == 'a':
            for doc in postings_list:
                postings_list[doc] = round(0.5 + (0.5*postings_list[doc] / max(postings_list.values())),2)
        elif self.ranking[0] == 'b':
            for doc in postings_list:
                postings_list[doc] = 1
        elif self.ranking[0] == 'L':
            for doc in postings_list:
                postings_list[doc] = round((1 + math.log(postings_list[doc])) / (1 + math.avg(postings_list.values())),2)
            
        return postings_list
        

    def doc_frequency(self,postings_list):
        if self.ranking[1] == 'n':
            return 1
        elif self.ranking[1] == 't' or self.ranking=="bm25":
            return round(math.log(self.doc_id / len(postings_list)),2)
        elif self.ranking[1] == 'p':
            return round(max(0, math.log(self.doc_id-len(postings_list)/len(postings_list))),2)
 
    def merge_files(self,out_file, final_file,i, init=0):
        
        # write all lines from all temporary segments in order to temp file
        with open("temp"+out_file, 'w+') as output_file:
            open_files = [open((str(n) + ".").join(out_file.split('.'))) for n in range(init,i+1)]
            output_file.writelines(heapq.merge(*open_files))
            [f.close() for f in open_files]

        [os.remove((str(n) + ".").join(out_file.split('.'))) for n in range(init,i+1)]

        # write to final output file the temporary file merge result
        with open("temp"+out_file, 'r') as temp_file, open(final_file,'w') as output_file:
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

        os.remove("temp"+out_file)

    def merge_and_compute_weights(self,out_file, final_file,i, init=0):
        
        # write all lines from all temporary segments in order to temp file
        with open("temp"+out_file, 'w+') as output_file:
            open_files = [open((str(n) + ".").join(out_file.split('.'))) for n in range(init,i+1)]
            output_file.writelines(heapq.merge(*open_files))
            [f.close() for f in open_files]

        [os.remove((str(n) + ".").join(out_file.split('.'))) for n in range(init,i+1)]

        # write to final output file the temporary file merge result
        with open("temp"+out_file, 'r') as temp_file, open(final_file,'w') as output_file:
            term = ""
            postings_list = dict()
            for line in temp_file:
                contents = line.split()
                if term:
                    if contents[0] == term:
                        term_content= contents[1:]
                        for term_i in term_content: # iterating over doc+freq for this term
                            term_i=term_i.split(":") #[doc,freq]
                            term_info[term_i[0]]= term_info.get(term_i[0],0)+ int(term_i[1].replace(",","")) #searching for doc in postings list and add frequency
                    else:
                        # change term_info = postings lists 
                        term_info = self.term_weight(term_info)
                        output_file.writelines(str(self.doc_frequency(term_info)) + ';' + str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                        output_file.writelines("\n")
                        term = contents[0]
                        term_info= contents[1:]
                        term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info}
                        output_file.write(contents[0] + ":")
                else:
                    term = contents[0]
                    term_info= contents[1:]
                    term_info={item.split(":")[0]:int(item.split(":")[1].replace(",","")) for item in term_info}
                    output_file.write(contents[0] + ":")
            if term:
                term_info = self.term_weight(term_info)
                output_file.writelines(str(self.doc_frequency(term_info)) + ';' + str(term_info).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":"))
                output_file.writelines("\n")

        os.remove("temp"+out_file)


    def finalize(self, out_file):

        sep = str(self.i) + "."
        output_file=open(sep.join(out_file.split('.')), "w")
        
        #writing the ordered dict in the file
        for key in sorted(self.dictionary.keys()):
            output_file.write(key + " " + str(self.dictionary[key]).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":") + "\n")
        
        output_file.close()

        file_threashold= resource.getrlimit(resource.RLIMIT_NOFILE)[0]//2

        #merge segments, do it in two times if the number of segments is to high
        if self.i < file_threashold:
            self.merge_and_compute_weights(out_file, out_file, self.i)
        else:
            j=0
            for j in range((self.i//file_threashold)):
                self.merge_files(out_file,(str(j) + ".").join(out_file.split('.')),(j+1)*(file_threashold)-1, j*(file_threashold))
            self.merge_files(out_file,(str(j+1) + ".").join(out_file.split('.')),self.i,(j+1)*(file_threashold))
            self.merge_and_compute_weights(out_file,out_file,j+1 )

        print(f'Temporary index segments: {self.i}')

    
    def indexer(self, docs, out_file, threshold, length, stopwords, p):

        #tokanization and stemmig of the documents 
        documents = {key:self.stemmer.stem(self.tokenizer.tokenize(text, filter=length, option=stopwords), option=p) for key,text in docs.items()}

        for doc_id,token_list in documents.items():
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
                output_file=open(sep.join(out_file.split('.')), "w")
                
                #writing the ordered dict in the file
                for key in sorted(self.dictionary.keys()):
                    output_file.write(key + " " + str(self.dictionary[key]).replace("\"","").replace("'","").replace("{","").replace("}","").replace(": ",":") + "\n")
                
                output_file.close()
                self.dictionary=dict()
                self.npostings=0
                self.i+=1

        return self.dictionary