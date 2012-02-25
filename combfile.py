"""

@Author: Madhura Raju (rmadhura@seas.upenn.edu) 
Program to perform topic proportion calculations on documents to perform content selection for multi-document summarization


"""
# Importing necessary packages/tools

from __future__ import division;
from nltk.tokenize import sent_tokenize
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import sent_tokenize
from numpy import array, zeros
from numpy import nan_to_num
from pageRank import pageRank
import operator
import nltk
import numpy

# Arithmetic helper functions
def add(x,y): return x+y
def elementwiseDivision(lst,val): return [x/val for x in lst]
def normalizeVector(proportions): return elementwiseDivision(proportions,reduce(add,proportions))

# Text helper functions
def tokenizeTextToSentences(text): return sent_tokenize(text)

def tokenizeCustomTextToSentences(text): return text.split('|')

# Topic proportions for intersection computation
topic_proportions = dict()
sentences = []

def readWordProportionsToDict(proportions_file):
	inp_file = open(proportions_file)
	
	prop_dict = {}
	
	for line in inp_file:
		tokens = line.strip().split('\t')
		prop_dict[tokens[0]] = [float(x) for x in tokens[1].strip().split(',')]
		#print tokens[0],"\t",prop_dict[tokens[0]]
		#raw_input()
	
	return prop_dict

"""
@inputparams:

document(string) -> the document to calculate word proportions for every sentence in it
word_proportions(dict k:string, val:float array) -> the dictionary which has words as its keys and float arrays as its values

@outputvals:

sentence_proportions (dict k:"sentence", val:float array) -> the proportions for that sentence
document_proportion (float array) -> topic proportion for the whole document as a whole

"""
def getTopicProportionsForSentences(document,word_proportions):
	
	document_proportion = zeros(5)
	sentence_proportions = {}
	tokenized_sentences = tokenizeTextToSentences(document)
	
	for sentence in tokenized_sentences:
		tokens = sentence.strip().lower().split(' ')
		
		# replace this magic number 10 by num_topics which you will define as a paramenter later.
		sent_prop = zeros(5)
		
		for tok in tokens:
			if tok in word_proportions.keys():
				sent_prop += word_proportions[tok]

		#print sentence,"\t",sent_prop
		#raw_input()
		
		document_proportion += sent_prop
		sentence_proportions[sentence] = normalizeVector(sent_prop)
	
	#print sentence_proportions
	#raw_input()
	
	return sentence_proportions,normalizeVector(document_proportion)
	
	
"""
Get the document wise proportions for the whole corpus

"""
def getTopicProportionsForCorpus(articles_path,word_proportions):

	sent_proportions = []
	document_proportions = []

	corpus_proportions = zeros(5)
	
	file_id = 0
	files = PlaintextCorpusReader(articles_path, '.*')
	ids = files.fileids()
	for i in range(0,len(ids)):
		current_file = articles_path + '/' + ids[i]
		sent_props,doc_prop =getTopicProportionsForSentences(open(current_file).read(),word_proportions)
		sent_proportions.append(sent_props)
		document_proportions.append(doc_prop)
		corpus_proportions += doc_prop

		#if i == 3:
			#break
		#print sent_proportions
		#print "For document ", str(i), " the proportions are ", doc_prop
		#raw_input()
	final_corpus_proportion = normalizeVector(corpus_proportions)
	return sent_proportions,document_proportions,final_corpus_proportion
		

def printWordProportionsToFile(dictionary_file,proportions_file,output_file):
	file_dicti = open(dictionary_file,'r')
	file_dict_words = open(output_file,'w')
	testlambda = numpy.loadtxt(proportions_file)
	
	ii = 0
	for word in file_dicti:
		file_dict_words.write(word.strip()+'\t'+','.join([str(x) for x in normalizeVector(list(testlambda[:,ii]))])+"\n")
		ii += 1
	
# Extracting the Entities from the sentences based on Part of Speech	
def getSentenceEntityList(sentence_filename):
	
	sent_ind = 0
	entityInd = 0
	entityDict = {}
	sent_entity = {}
	
	for sents in open(sentence_filename,'r'):
		tokens = sents.strip().split('\t')
		tags = nltk.pos_tag(tokens[0].strip().split())
		topic_proportions[sent_ind] = [float(x) for x in tokens[1:]]
		#print tokens[0]
		#raw_input()
		
		sentences.append(tokens[0])
		sent_entity[sent_ind] = []
		
		for tag in tags:
			if tag[1] == "NNP" or tag[1] == "NN":
		
				ttag = tag[0].lower()
			
				if ttag[-1] in [',','.',';,','\'','\"']:
					ttag = ttag[0:-1]
			
				if ttag not in entityDict.keys():
					entityDict[ttag] = entityInd
					#print tag[0].lower(), entityInd
					entityInd += 1
				
				sent_entity[sent_ind].append(entityDict[ttag])


		sent_ind += 1
	return entityDict, sent_entity
	
def intersection(sent1,sent2):
	found = False
	
	if len(sent1[1]) == 0 or len(sent2[1]) == 0:
		return 0.0
	
	for w1 in sent1[1]:
		if w1 in sent2[1]:
			found = True
			break;		
	if found:
		return ExtendedJaccard(topic_proportions[sent1[0]],topic_proportions[sent2[0]])
	else:
		return 0.0
		
# Performing extended JaccardSimilarity 
def ExtendedJaccard(sent1,sent2):
	if len(sent1) != len(sent2):
		return 0.0
	if len(sent1) == 0 or len(sent2) == 0:
		return 0.0
	val =  (numpy.sum(numpy.minimum(sent1,sent2)))/(numpy.sum(numpy.maximum(sent1,sent2)))
	return val
	
# to format the input to the pagerank algorithm
def inputforPageRank(sent_entities):
	mtrix = []
	
	for k1,v1 in sent_entities.iteritems():
		for_sent = []
		for k2, v2 in sent_entities.iteritems():
			if k1 == k2:
				for_sent.append(0.0)
				continue
		
			for_sent.append(intersection((k1,v1),(k2,v2)))
		mtrix.append(list(normalizeVector(array(for_sent))))
	
	return nan_to_num(array(mtrix))
	
def rankbyPageRank(norm_pRank):
	sents_withPR = {}
	zipped_pRank_Sents = zip(sentences,norm_pRank)
	sorted_pRank = sorted(zipped_pRank_Sents, key = operator.itemgetter(1), reverse = True)
	return sorted_pRank

#Uses the output from the LDA and the VariationalApproximation files, that gives the word clusters and the probability associated with every word.	
if __name__ == '__main__':
	printWordProportionsToFile('dicti.txt','nlambda-190.dat','dictwords.txt')
	word_props = readWordProportionsToDict('dictwords.txt')
	sent_outfile = open('sent_proportions.txt','w')
	sent_proportions, document_proportions, corpus_proportions = getTopicProportionsForCorpus('C:\Users\madhura\Desktop\lda_modelling\d30007t',word_props)
	
	for doc_sentences in sent_proportions:
		for k,v in doc_sentences.iteritems():
			sent_outfile.write(k.replace('\n','')+"\t"+'\t'.join(str(x) for x in v) + "\n")
	sent_entities = []
	i = 0
	ranked_finals = ''
	entityDict, sent_entity = getSentenceEntityList('sent_proportions.txt')
	#for k,v in sent_entity.iteritems():
	#	print k,v
	#	sent_entities.append(v)
	pageRankInput = inputforPageRank(sent_entity)
	raw_input()
	norm_pageRank = pageRank(pageRankInput,s=.86)
	ranked_sentences = []
	#print norm_pageRank
	ranked_final = rankbyPageRank(norm_pageRank)
	for every_el in ranked_final:
		ranked_sentences.append(every_el[0])
	#ranked_sentences = set(ranked_sentences)
	
	#print ranked_sentences
	#raw_input()
	unique_sentences = []
	
	for rs in ranked_sentences:
		if rs not in unique_sentences:
			unique_sentences.append(rs)
						
	for sents in unique_sentences:
		if i<=10:
			ranked_finals = ranked_finals + sents
			i += 1
	print ranked_finals
	outputfile = open('collection_7.txt','w')
	for w in ranked_finals:
		outputfile.write(w)
	
	
