"""
Information Retrieval Assignment 1 2021/2022
Authors: Alexandra Carvalho, Margarida Martins

Class Index
"""

import psutil
import os
import heapq
import resource

from tokenizer import Tokenizer
from porter_stemmer import PorterStemmer


class Index:

    def __init__(self):
        self.dictionary = dict()
        self.npostings=0
        self.i = 0
        self.doc_id = 0

        self.tokenizer = Tokenizer()
        self.stemmer = PorterStemmer()
 
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
            self.merge_files(out_file, out_file, self.i)
        else:
            j=0
            for j in range((self.i//file_threashold)):
                self.merge_files(out_file,(str(j) + ".").join(out_file.split('.')),(j+1)*(file_threashold)-1, j*(file_threashold))
            self.merge_files(out_file,(str(j+1) + ".").join(out_file.split('.')),self.i,(j+1)*(file_threashold))
            self.merge_files(out_file,out_file,j+1 )

        print(f'Temporary index segments: {self.i}')

    
    def indexer(self, docs, out_file, threshold, length, stopwords, p):

        #tokanization and stemmig of the documents 
        documents = {key:self.stemmer.stem(self.tokenizer.tokenize(text, filter=length, option=stopwords), option=p) for key,text in docs.items()}

        for doc_id,token_list in documents.items():
            pos=0
            self.doc_id += 1
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