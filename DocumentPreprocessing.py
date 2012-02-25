"""

@Author: Madhura Raju (rmadhura@seas.upenn.edu) 
Program to clean the text, remove stop words, etc.

"""

class DocumentPreprocess:
    
    """
    Contains general functions which will be useful for text preprocessing.
    """
    
    # Add characters to this list if you want to completely strip them out of every string
    clean_list = ['"',"'","?","+","-","*","&","^","%","$","#","@","!","~","`"]
    
    #Add special characters to this list if you want to treat them as special delimiters and replace them by a whitespace
    delimiter_list = [".",",",";",":","(",")","{","}","[","]","|","<",">"]
    
    def readSingleTokenTextFile(self,input_file):
        """
        returns a list of words in the file
        """
        word_list   =   []
        for line in input_file:
            word_list.append(line.strip())
        return word_list
    
    
    def constructWordFrequencyDict(self,word_list):
        """
        @input:     word_list 
        @retval:    dictionary of words -> num_counts
        """
        word_dict = dict()
        for word in word_list:
            if word_dict.has_key(word):
                word_dict[word] += 1
            else:
                word_dict[word] = 1
        return word_dict
    
    def cleanWord(self,word):
        """
        removes special characters as defined by clean_list and lowercases all characters 
        @input: raw word
        @output: sanitized word
        """
        clean_dict      =   self.constructWordFrequencyDict(self.clean_list)
        final_chars     =   []
    
        for char in word:
            
            if clean_dict.has_key(char):
                continue
            else:
                final_chars.append(char)
        
        return "".join(final_chars)
    
    
    def returnCleanWordListFromText(self,free_text):
        """
        @input: free_text is a string containing text which needs cleaning up.
        @output: list of cleaned up lowercased words from the free text 
        @note: The delimiters are governed by the member variable, delimiter_list
        """
        tmp_free_text   =   free_text.lower()
        final_word_list =   []
        
        
        for char in self.delimiter_list:
            tmp_free_text = tmp_free_text.replace(char," ")
        
        for word in tmp_free_text.strip().split(" "):
            
            cleaned_word = self.cleanWord(word)
            if cleaned_word != " " and cleaned_word != '' and cleaned_word.isalpha():
                final_word_list.append(self.cleanWord(word)) 
                
        return final_word_list
        
        
    def removeTheseWords(self,original_list,to_be_removed):
        """
        @input: origial_list of words
        @input: to_be_removed words
        @Note: List order is not maintained.
        """
        
        original_dict   =   self.constructWordFrequencyDict(original_list)
        removals_dict   =   self.constructWordFrequencyDict(to_be_removed)
        
        for key in removals_dict.keys():
            if original_dict.has_key(key):
                del original_dict[key]
                
        # Recreating a list from the dictionary
        final_list = []    
        for key,val in original_dict.iteritems():
            for ii in range(0,int(val)):
                final_list.append(key)
        
        return final_list

    
    def mapWordListToNumbers(self,word_list,word_mapping):
        """
        @input: word_list should be a list of strings which need mappings to integers
        @input: word_mapping should be a dictionary of word -> integer
        @output: a list of numbers representing words in a document and counts of those words in the document
        @note: if word is not found in the mapping, it will not be mapped
        
        """
        count_list      =   dict()
        words_list      =   []
        word_counts     =   []
        mapping         =   0
        
        for word in word_list:
            if word_mapping.has_key(word):
                mapping = word_mapping[word]
                if count_list.has_key(mapping):
                    count_list[mapping] += 1
                else:
                    count_list[mapping] = 1
                                              
        for k,v in count_list.iteritems():
            words_list.append(k)
            word_counts.append(v)
        
        return words_list, word_counts
    
    
    def readTSVDocs(self,input_file,stopwords_file,dict_file):
        """
        @input: input_file      ->  TSV file of the format <document_identifier>     <raw text in the document>"\n"
        @input: stopwords_file  ->  text file containing a stopword at each line.
        @output: dictionary_mapping.txt ->  the file which will have the word to numbers mapping for future usage.
        @retval: a dictionary of docIDs -> list of words(numbers) in the corpus
        @Note: All words are lowercased completely and mapped to an integer and written into a txt file for further usage.   
        
        """
        
        # map words to numbers for ease of computation and less storage
        word_mappings   =   dict()
        num_wordmapping =   dict()
        documents       =   dict() 
        doc_freq        =   dict()
        doc_id          =   ""
        free_text       =   ""
        word_list       =   []
        doc_words       =   []
        stopwords       =   self.readSingleTokenTextFile(open(stopwords_file))
        word_id         =   0
        num_docs        =   1
        
        for line in open(input_file):
            
            # Find the doc_id which is the set of characters before the first tab
            tmp_doc_id = []
            break_location = 0
            
            for char in line:
                if char != '\t':
                    tmp_doc_id.append(char)
                    break_location += 1
                else:
                    break
            doc_id = "".join(line[0:break_location])
            
            # the free text of the document is everthing after the first tab
            free_text = line[break_location+1:]
        
            # constructing the word list from the free text
            word_list = self.removeTheseWords(self.returnCleanWordListFromText(free_text),stopwords)
            
            #adding the newly seen words to the word-to-numbers map
            for word in word_list:
                if word_mappings.has_key(word):
                    continue
                else:
                    word_mappings[word] = word_id
                    num_wordmapping[word_id] = word
                    word_id += 1
            
            #getting the list of numbers mapped from words
            doc_words,doc_word_freq = self.mapWordListToNumbers(word_list,word_mappings)
            
            #creating the doc_id -> word_list entry
            documents[num_docs-1] = doc_words
            doc_freq[num_docs-1] = doc_word_freq

            print "Read document :",num_docs," with id ",doc_id," having ",len(doc_words)," words..."
            num_docs += 1
            
        # Writing the word -> number mappings to the dictionary.txt file.
        
        dictionary_file = open(dict_file,"w")
        
        for ii in xrange(0,len(num_wordmapping)):
            dictionary_file.write(num_wordmapping[ii]+"\n")
                        
        return documents, doc_freq, dict_file
        

if __name__ == '__main__':
    
    x = DocumentPreprocessing()
    documents, doc_freq = x.readTSVDocs("sampleCorpus.txt","stopword.txt","dicty.txt")
    # print documents
    # print doc_freq
