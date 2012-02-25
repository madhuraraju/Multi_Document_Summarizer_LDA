"""

@Author: Madhura Raju (rmadhura@seas.upenn.edu) 
Program to combine all the documents in a particular collection, which is the input to the lda.py

"""

import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import sent_tokenize

def article_merge(articles_path):
	file_id = 0
	files = PlaintextCorpusReader(articles_path, '.*')
	ids = files.fileids()
	sent_collections = []
	file_input = open('d30007t_input.txt','w')
	sent_file = open('inputForCombFile.txt','w')
	
	for i in range(0,len(ids)):
		current_file = articles_path + '/' + ids[i]
		sent_collections.append(load_file_sentences(current_file))
		file_id += 1
		file_input.write(str(file_id) + "\t" + " ".join(sent_collections[i]))
		file_input.write('\n')
		sent_file.write(str(file_id)+"\t"+ '|'.join(sent_collections[i]))
		sent_file.write('\n')
		
def load_file_sentences(path):
	tokenized_sents = []
	sents_new = []
	file_sent = open(path,'r')
    #all_sents = file_sent.read().replace('\n','').lower()
	tokenized_sents = sent_tokenize(file_sent.read())
	for every_sents in tokenized_sents:
		sents_new.append(every_sents.replace('\n','').lower())
	return sents_new
	
if __name__ == '__main__':
	#article_merge('''\C:\Users\madhura\Desktop\articles\d30006t''')
	article_merge('d30007t')
