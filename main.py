# Importing Libraries

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
from natsort import natsorted
import math

#######################################(First Part)#######################################


# 1.Read Files:-

# files names sorted
ls_documents = [] 
for name in natsorted(os.listdir("Collection/")):
    ls_documents.append(name)

# files content
ls_text = []
for document in ls_documents[:10]:
    file_content = open("Collection/" + document,"r")
    ls_text.append(file_content.read())
    

# 2.Apply Tokenization:-

tokens = [word_tokenize(i) for i in ls_text]


# 3.Apply Stop Words:-

stop_words = set(stopwords.words('english'))

clean_models = []
for m in tokens:
    clean_list = [i for i in m if str(i).lower() not in stop_words]
    clean_models.append(clean_list)


#######################################(Second Part)#######################################


# 1.Build Positional Index:-

# we started docs ids from 1 not 0
doc_id = 1
positional_index = {}

# loop on tokens(all documents) to work on document by document
for doc_content in tokens:
    
    # loop on terms in each document
    for position, term in enumerate(doc_content):
        
        # check if term wrote before in positional index
        if term in positional_index:
                         
            # check if the term has existed in that doc_id before then append the position at the existing doc
            # if the term existed in the same row(document) more than 1 time
            if doc_id in positional_index[term][1]:
                positional_index[term][1][doc_id].append(position)
            # else if the doc_id is new then initialize new doc positions
            else:
                positional_index[term][1][doc_id] = [position]
                # increment doc frequency by 1.
                positional_index[term][0] = positional_index[term][0] + 1
        # else if term does not exist in the positional index dictionary
        else:
                         
            # initialize the list by writing the new term.
            positional_index[term] = []
            # as it's new then doc frequency will be 1.
            positional_index[term].append(1)
            # the postings list is initially empty.
            positional_index[term].append({})     
            # add doc_id to postings list.
            positional_index[term][1][doc_id] = [position]

    # increment doc_id by 1
    doc_id = doc_id + 1


# Display Each Term:-

for key in positional_index:
    print()
    print("-------------------------- Term:" , key , "--------------------------")
    print()
    print("<" , key , "," , positional_index[key][0] , ";")
    display_iterative = 0
    for k in list(positional_index[key][1].keys()):
        print(k , ":" , list(positional_index[key][1].values())[display_iterative] , ";")
        display_iterative = display_iterative + 1
    print(">")

#-----------------------------------------------------------------------------------------------------------------#

# 2.Phrase Query:-

# to get phrase from user to retrieve documents
phrase = input("Enter Phrase you want to search for: ")

# split phrase query to tokens
query_tokens = word_tokenize(phrase)

# transform tokens to lowercase
queries_lower = []
for term in query_tokens:
    queries_lower.append(term.lower())

# remove stop words from query
'''
clean_query = []
for m in queries_lower:
    if m not in stop_words:
        clean_query.append(m)
'''        
#---------------------------------------------------------------------------------------------------------#
# function that triggered when phrase contains only one term
def one_term_phrase(term): 
    
    ResultSet = {}
    print("Term (" , term , ") after preprocessing exists at:-")
    print("Documents : Positions")
    i=0
    for doc in list(positional_index[term][1].keys()):
        ResultSet[doc] = []
        ResultSet[doc].extend(list(positional_index[term][1].values())[i])                
        print(doc , ":" , list(positional_index[term][1].values())[i])
        i = i+1

    return ResultSet

#---------------------------------------------------------------------------------------------------------#
# function that triggered when phrase contains more than one term and they exist in positional index
def match_phrase(term1_postings , term2_postings):
    
    # result set that match 2 terms posting list sequence
    new_result_set = {}
    
    # pointer on each document in first term posting list
    doc_iterative1 = 0
    # pointer on each document in second term posting list
    doc_iterative2 = 0
    
    # pointer on position in each document in first term posting list
    positions_iterative1 = 0
    # pointer on position in each document in second term posting list
    positions_iterative2 = 0
    
    # while we didn't reach end of any term posting list (end of document numbers)
    while( doc_iterative1 < len(term1_postings) and doc_iterative2 < len(term2_postings) ):
        
        # if document number in first term posting list = document number in second term posting list then compare positions
        if list(term1_postings.keys())[doc_iterative1] == list(term2_postings.keys())[doc_iterative2]:
            
            # while we didn't reach end of any position list in each document in posting list
            while( positions_iterative1 < len(list(term1_postings.values())[doc_iterative1]) and positions_iterative2 < len(list(term2_postings.values())[doc_iterative2]) ):
                
                # in case that position in document number in first term posting list + 1  =  position in same document number in second term posting list
                # then add this document and this position to new_result_set dictionary
                if list(term1_postings.values())[doc_iterative1][positions_iterative1] + 1 == list(term2_postings.values())[doc_iterative2][positions_iterative2]:
                    new_result_set[list(term2_postings.keys())[doc_iterative2]] = []
                    new_result_set[list(term2_postings.keys())[doc_iterative2]].append(list(term2_postings.values())[doc_iterative2][positions_iterative2])
                
                # in case that position in document number in first term posting list > position in same document number in second term posting list 
                # then move pointer of second term position list to next position
                elif list(term1_postings.values())[doc_iterative1][positions_iterative1] > list(term2_postings.values())[doc_iterative2][positions_iterative2]:
                    positions_iterative2 = positions_iterative2+1
                
                # in case that position in document number in first term posting list < position in same document number in second term posting list
                # then move pointer of first term position list to next position
                else:
                    positions_iterative1 = positions_iterative1+1
                    
                # go to next position iteration
                positions_iterative1 = positions_iterative1+1
                positions_iterative2 = positions_iterative2+1
            # move to next doc in two posting lists
            doc_iterative1 = doc_iterative1+1
            doc_iterative2 = doc_iterative2+1
            
            # return vals to zero to move to new posting lists
            positions_iterative1 = 0
            positions_iterative2 = 0
            
        # if document number in first term posting list > document number in second term posting list
        # then move to next doc in second posting lists
        elif list(term1_postings.keys())[doc_iterative1] > list(term2_postings.keys())[doc_iterative2]:
            doc_iterative2 = doc_iterative2+1
        
        # if document number in first term posting list < document number in second term posting list
        # then move to next doc in first posting lists
        else:
            doc_iterative1 = doc_iterative1+1
            
    # at the end return the result set
    ResultSet = new_result_set
    return ResultSet

#---------------------------------------------------------------------------------------------------------#
# ResultSet that display which documents will contain phrase query
ResultSet = {}
# 0 if all words exist in positional index and 1 if there is any word doesn't exist in positional index
flag = 0

# in case that phrase contains more than one word 
if len(queries_lower) > 1:
    for term in queries_lower:
        if term not in positional_index:
            print("No Matched Docs")
            flag = 1
            break
    if flag == 0:
        # we will compare two terms for many times equal length of phrase terms (if terms are 4 then we will compare 3 times)
        for i in range(0, len(queries_lower)-1):
            # at first iteration send first term posting list in Query as a first term posting list
            if i == 0:
                ResultSet = match_phrase(positional_index[queries_lower[0]][1] , positional_index[queries_lower[1]][1])  
            # at any iteration send returned result set as a first term posting list
            else:
                ResultSet = match_phrase(ResultSet , positional_index[queries_lower[i+1]][1]) 
    # if resultset is not null print it
    if ResultSet:
        print("Phrase (" , phrase , ") after preprocessing exists at:-")
        print("Documents : Positions")
        i=0
        for doc in list(ResultSet.keys()):
            print(doc , ":" , list(ResultSet.values())[i])
            i = i+1
        # to print result set
        #print(ResultSet)
    else:
        print("No Matching in positional index")
        
# in case that phrase contains only one word 
elif len(queries_lower) == 1:
    if term not in positional_index:
        print("No Matched Docs")
        flag = 1
    else:
        ResultSet = one_term_phrase(queries_lower[0])
# in case that phrase contains no words (or words removed by stop words)
else:
    print("you should enter a word")
    

#######################################(Third Part)#######################################


# 1.Compute term frequency for each term in each document:-

#  if flag = 0, all words exist in collection 
if flag == 0:

    def calculate_term_freq(term , document):
        count = 0
        for compared_term in document:
            if compared_term == term:
                count = count+1
        return count
    
    def calculate_term_freq_weight(count):
        if count > 0:
            return (1 + math.log(count,10))
            #return "{:.1f}".format((1 + math.log(count,10)))
        else:
            return 0.0;
    
    term_frequency = {}
    term_frequency_weight = {}
    
    for term in positional_index:
        term_frequency[term] = []
        term_frequency_weight[term] = []
        count = 0
        weight = 0
        for i in range(0, len(tokens)):
            count = calculate_term_freq(term , tokens[i])
            weight = calculate_term_freq_weight(count)
            term_frequency[term].append(count)
            term_frequency_weight[term].append(weight)
    
    print()
    print("---------------------------(Term Frequency)---------------------------")
    print()
    for i in range(0, len(tokens)):
        print(i+1 , end="\t")
    print(":Doc Num")
    print()
    
    for term in term_frequency:
        for term_count in term_frequency[term]:
            print(term_count,end = "\t")
        print(":" , term , end="")
        print()
    
    
    print()
    print("------------------------(Term Frequency Weight)------------------------")
    print()
    for i in range(0, len(tokens)):
        print(i+1 , end="    ")
    print(":Doc Num")
    print()
    
    for term in term_frequency_weight:
        for term_weight in term_frequency_weight[term]:
            print(term_weight,end = "  ")
        print(":" , term , end="")
        print()
    
    
# 2.Compute IDF for each term:-
    
    
    df_idf = {}
    num_of_docs = len(tokens)
    
    for term in positional_index:
        df_idf[term] = []
        df = positional_index[term][0]
        df_idf[term].append(df)
        idf = math.log(num_of_docs/df,10)
        #idf = "{:.1f}".format(math.log(num_of_docs/df,10))
        df_idf[term].append(idf)
        
    
    print()
    print("---------------------------(DF & IDF)---------------------------")
    print()
    print("df\tidf")
    print()
    
    for term in df_idf:
        for term_count in df_idf[term]:
            print(term_count,end = "\t")
        print(":" , term , end="")
        print()
    
    
# 3.Displays TF.IDF matrix:-
    
    
    tf_idf = {}
    
    for term in term_frequency_weight:
        tf_idf[term] = []
        tf_idf_val = 0.0
        for w_tf in term_frequency_weight[term]:
            tf_idf_val = w_tf * df_idf[term][1]
            tf_idf[term].append(tf_idf_val)
    
    print()    
    print("------------------------(TF-IDF)------------------------")
    print()
    for i in range(0, len(tokens)):
        print(i+1 , end="       ")
    print(":Doc Num")
    print()
    
    for term in tf_idf:
        for term_tf_idf in tf_idf[term]:
            print("{:.4f}".format(term_tf_idf),end = "  ")
        print(":" , term , end="")
        print()
    
    
    # 4.Compute cosine similarity:-
    
    #calculate document length
    doc_length = []
    for i in range(0, len(tokens)):
        # initialize doc_sum_square to store sum of multiply of square of tf and idf of document 
        doc_sum_square = 0
        for x in tf_idf:
            doc_sum_square = doc_sum_square + tf_idf[x][i]**2     
        doc_length.append(math.sqrt(doc_sum_square)) 
    
    print()    
    print("------------------------(Documents List)------------------------")
    print()
    for i in range(0, len(doc_length)):
        print("Doc",i+1 , " Length:- " , end="  ")
        print(doc_length[i])


    # calculate normalize for every document 
    doc_norm = {}
    # iterate on each column
    for i in range(0, len(doc_length)):
        doc_norm[i]=[]
        for x in tf_idf:
            #normalize = tf*idf / doc_length
            doc_norm[i].append(tf_idf[x][i]/doc_length[i] ) 
        
        
    # Display normalized of every document with each term:-

    # pointer on doc_norm in each document 
    iterative = 0 
    # initialize the list by writing the new term.   
    term_doc_norm={}        
    for term in term_frequency:
        term_doc_norm[term]=[]    
        for i in range(0, len(doc_norm)):
            term_doc_norm[term].append(doc_norm[i][iterative])          
        iterative=iterative+1
      
    print()    
    print("------------------------(Normalized TF-IDF)------------------------")
    print()
    for i in range(0, len(tokens)):
        print(i+1 , end="       ")
    print(":Doc Num")
    print()
    
    for term in term_doc_norm:
        for term_norm_tf_idf in term_doc_norm[term]:
            print("{:.4f}".format(term_norm_tf_idf),end = "  ")
        print(":" , term , end="")
        print()
        
        
    ###################### query information ######################    

    # TF of query 
    query_term_frequency={}
    # TFw of query
    query_term_frequency_weight={}
    for term in queries_lower:
        # if term in queries_lower and positional_index 
        if term in positional_index:
            query_term_frequency[term] = 0
            query_term_frequency_weight[term] = 0
            query_count = 0
            query_weight = 0
            query_count = calculate_term_freq(term , queries_lower)
            query_weight = calculate_term_freq_weight(query_count)
            query_term_frequency[term]=query_count
            query_term_frequency_weight[term]=query_weight     
    
    # Calculate idf of term in query
    num_of_docs = len(tokens)
    query_idf={}
    for term in queries_lower:
        if term in df_idf:
            query_idf[term]=df_idf[term][1]
            
    # Calculate tf * idf of term in query
    query_tf_idf={}
    for term in queries_lower:
        query_tf_idf[term]=query_term_frequency_weight[term]*query_idf[term]
    
    
    # Calculate query length
    # initialize query_sum_square to store sum of multiply of tf and idf of query 
    query_sum_square = 0
    for x in query_tf_idf:
        query_sum_square = query_sum_square + query_tf_idf[x]**2    
    query_length = math.sqrt(query_sum_square)
    
    
    #calculate normalize for each term in query
    query_term_doc_norm = {} 
    # initialize query_res_sum to store the remainder of the division from query_tf_idf[term] on query_length
    query_res_sum = 0
    
    for term in queries_lower:
        query_res_sum =  query_tf_idf[term]/query_length     
        query_term_doc_norm[term] = query_res_sum 
        
        
    #print data of query
    
    queries_info = {}
    for term in queries_lower:
        queries_info[term]={}
        queries_info[term]["TF"] = query_term_frequency[term]
        queries_info[term]["TFW"] = query_term_frequency_weight[term]
        queries_info[term]["IDF"] = query_idf[term]
        queries_info[term]["WT"] = query_tf_idf[term]
        queries_info[term]["Normalized"] = query_term_doc_norm[term]
        
    
    print()    
    print("------------------------(Query Information)------------------------")
    print()
    print("TF \t TFW \t IDF \t WT   Normalized  :Difference")
    print()
    
    for term in queries_info:
        print(queries_info[term]["TF"] , end="   ")
        print("{:.3f}".format(queries_info[term]["TFW"]) , end="   ")
        print("{:.3f}".format(queries_info[term]["IDF"]) , end="   ")
        print("{:.3f}".format(queries_info[term]["WT"]) , end="   ")
        print("{:.3f}".format(queries_info[term]["Normalized"]) , end="    ")
        print(":" , term , end="")
        print()
    
    
    #calculate product for each term in query of every document   
    product = {}
    for term in queries_lower:
        product[term]=[]
        for i in range(0, len(tokens)):
            # initialize product_multiplication to store multiply of normalize of term on query and normalize of every document
            product_multiplication = query_term_doc_norm[term] *term_doc_norm[term][i] 
            product[term].append(product_multiplication)
    
    #calculate score (cosine simlarity)
    score = {}
    for i in range(0, len(tokens)):
        # initialize score_sum to store sum of product for each document
        score_sum = 0
        for term in product:
            score_sum = score_sum + product[term][i]
        # to store docid (1 to 10) as we did in positional index    
        score[i+1]=score_sum
        
        
    #.5. rank documents based on cosine similarity 
    # display the score of term with documents in query
    clean_score_docs = {}
    for docid in ResultSet:
        if docid in score:
            clean_score_docs[docid] = score[docid]
            
    # The ranking of the documents with the highest score    
    sorted_rank =sorted(clean_score_docs.items(), key=lambda x:x[1], reverse=True)
    
    
print()
print("------------------------(Rank Documents Result)------------------------")
print()
#if result is not null, phrase query is in documents
if ResultSet != {}:
    print("rank of returned docs based on similarity is :-" )
    for doc_info in sorted_rank:
        print("Doc Id :" ,doc_info[0], "  Score :" ,doc_info[1] )
# if flag = 1, some words doesn't exist in collection of docs
elif flag == 1:
    print("no docs returned, because some words doesn't exist in collection of docs")
# in this case if docs docs don't contain this phrase
else:
    print("no docs returned, docs don't contain this phrase")


