# -*- coding: utf-8 -*-
"""InvertedIndexGrannlarityFinal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jQQxq6HHHO8icIXArLYGG_MKcSenFErp
"""

import os
from functools import reduce
import time
import gzip
import shutil
from numpy import arange
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import math as m

from lxml import etree
import lxml.html
import lxml.html.soupparser

from bs4 import BeautifulSoup as bs

_WORD_MIN_LENGTH = 0
_STOP_WORDS = {'or', 'very', 'any', "that'll", 'until', 'will', 'few', 'all', 'my', 'with', 'between', 'doesn', 'we',
               'why', 've', 'am', "wouldn't", 'only', 'i', 'couldn', 'been', "mightn't", 'for', "hadn't", 'on', 'did',
               'have', 'than', "weren't", 'wouldn', "you're", 'isn', "you've", 'such', 'y', 'his', 'after', 'me',
               'here', 'was', 'do', 'again', "it's", 'didn', 'once', 'he', 'hadn', "don't", 'had', 'itself', 'in',
               'ain', 'to', 'further', 'o', 'not', 'as', 'down', 'about', 'up', "needn't", 'its', 'above', 'theirs',
               'yourself', 'our', 'same', 'more', "shouldn't", 's', 'hasn', "won't", 'your', 'own', 'don', "wasn't",
               'which', 'over', "doesn't", 'under', 'weren', 'and', 'most', "you'd", 'were', 're', 'whom', "you'll",
               'because', 'from', 'should', 'the', 'needn', "haven't", 'where', 'she', 'her', 'that', 'this', 'at',
               'him', 'having', 'by', "didn't", 'their', 'during', 'below', 'each', 'yourselves', 'how', 'being', 'can',
               'what', 'hers', 'both', 'they', "isn't", 'ourselves', 'himself', 'nor', 'be', "should've", "aren't",
               "couldn't", 'won', 'who', 'themselves', 'now', "shan't", 'mustn', 'while', 'doing', 'you', 'herself',
               'so', 'a', 'm', 'has', 'then', 'if', 'some', 'no', 'yours', 'll', 'these', 'shan', 'them', 'haven', 'of',
               'just', 'there', "hasn't", "mustn't", 'out', 't', 'is', 'aren', 'wasn', 'into', 'against', 'but', 'too',
               'when', 'are', 'myself', 'shouldn', "she's", 'other', 'ours', 'does', 'through', 'ma', 'it', 'before',
               'mightn', 'off', 'an', 'd', 'those'}
TIME = 0

path_data_list = {}  #{"/docId/Article/Header":"text text text","/docId/Article":"text text text",...,"/docId/Article":..}
elementsList = ["article", "title", "bdy", "sec"]
charsToIdentifyElements = 2
overlapAllowed = False
DOCUMENT_WORDS = {}
DOCUMENT_LENGTHS = {}
STEMMER = False
STOP_WORDS = False
ALLOW_ENTRELACEMENT = True
WORD_COUNT = 0
INVERTED = {}
K = 1.2
B = 0.75
QUERY_RESULTS_LIMIT = 1500
TEAM = "YahyaYasserYounessIbtissam"
FILE_DIRECTORY = "XML-Coll-withSem"
FILE_LIST = [FILE_DIRECTORY + "/" + filename for filename in os.listdir(FILE_DIRECTORY)]
stop_words_filename = ""
parser = etree.XMLParser(recover=True)

def walkTreeForElemnts(document_path, elementsList):
    '''
    Takes an XML document path to extract "XPath" of all elements in elementsList as well as their content as text only and puts it in elementsPathTexts[docId]
    '''
    global path_data_list
    tree = etree.parse(document_path, parser=parser)
    docId = tree.getroot().find(".//id").text
    for elem in tree.iter():
        if (elem.tag in elementsList):
            textOnly = bs(etree.tostring(elem, encoding='utf8', method='xml')).get_text().replace('\n', ' ').replace('\r', '')
            xPath = tree.getpath(elem)
            hasChildren = False

            for element in elementsList:
                # searches for any descendent named "element"
                elemPath = ".//"+element
                elems = elem.xpath(elemPath)
                if len(elems)!=0 :
                    hasChildren = True

            # Adds [1] to the unique elements
            path = "/".join([element + "[1]" if element != '' and element[-1] != ']' else element for element in xPath.split('/')])

            #If overlapping isn't allowed and node doesn't have a child element in elements list add to path_data_list
            if not hasChildren and not overlapAllowed:
                path_data_list["/" + docId + path] = textOnly

def word_split(text):
    """
    Split a text into words. Returns a list of tuple that contains
    (word, occcurence)
    """
    word_list = []  # [[word,occurences],[,],[,]]
    word_occurence_dict = {}  # {word:occurences,word:occurences}
    wcurrent = []
    for c in text:
        if c.isalnum():
            wcurrent.append(c)
        elif wcurrent:
            word = u''.join(wcurrent)
            word = word.lower()
            if word not in word_occurence_dict.keys():
                word_occurence_dict[word] = 1
            else:
                word_occurence_dict[word] += 1
            wcurrent = []

    if wcurrent:
        word = u''.join(wcurrent)
        if word not in word_occurence_dict.keys():
            word_occurence_dict[word] = 1
        else:
            word_occurence_dict[word] += 1

    word_list = list(word_occurence_dict.items())

    return word_list


def stop_word_split(text):
    """
    Split a text in words. Returns a list of words.
    """
    word_list = []
    wcurrent = []

    for c in text:
        if c.isalnum():
            wcurrent.append(c)
        elif wcurrent:
            word = u''.join(wcurrent)
            word_list.append(word)
            wcurrent = []

    if wcurrent:
        word = u''.join(wcurrent)
        word_list.append(word)

    return word_list


def words_cleanup(words):
    """
    Remove words with length less then a minimum and stopwords.
    """
    clean_words = []
    for word, occurence in words:
        if len(word) <= _WORD_MIN_LENGTH or (STOP_WORDS and word in _STOP_WORDS):
            continue
        clean_words.append((word, occurence))
    return clean_words


def stem_word(word):
    if STEMMER:
        ps = PorterStemmer()
        word = ps.stem(word)
    return word


def words_normalize(words):
    """
    Do a normalization precess on words. In this case is just a lower() but we can add stemming here
    """
    normalized_words = []
    for word, occurence in words:
        wnormalized = word.lower()
        wnormalized = stem_word(word)
        normalized_words.append((wnormalized, occurence))
    return normalized_words


def word_index(doc_id, text):
    """
    Just a helper method to process a text.
    It calls word split, normalize and cleanup.
    """
    global WORD_COUNT,DOCUMENT_LENGTHS,DOCUMENT_WORDS
    words = word_split(text)
    words = words_normalize(words)
    words = words_cleanup(words)

    document_length = 0
    for word, occurence in words:
        document_length += occurence
    DOCUMENT_LENGTHS[doc_id] = document_length
    WORD_COUNT += document_length
    DOCUMENT_WORDS[doc_id] = words

    return words


def inverted_index(doc_id, text):
    """
    Create an Inverted-Index of the specified text document.
        {word:[locations]}
    """
    inverted = {}

    for word, index in word_index(doc_id, text):
        inverted.setdefault(word, 0)
        inverted[word] += index

    return inverted


def inverted_index_add(inverted, doc_id, doc_index):
    """
    Add Invertd-Index doc_index of the document doc_id to the
    Multi-Document Inverted-Index (inverted),
    using doc_id as document identifier.
        {word:{doc_id:[locations]}}
    """
    for word, locations in doc_index.items():
        indices = inverted.setdefault(word, {})
        indices[doc_id] = locations
    return inverted


def get_doc_data(path,data):
    return (path,data)


def stats(index):

    print("--- -document length : ", WORD_COUNT, " words")

    avg_term_length = 0
    for word in index.keys():
        avg_term_length += len(word)
    if len(index)>0:
      avg_term_length = avg_term_length / len(index)

    print("--- -average term length : ", avg_term_length, " characters")

    vocabulary_size = len(index)
    print("--- -vocabulary size : ", vocabulary_size, " words")

    print("--- -processing time : ", TIME, " seconds")


def unzip(file_name):
    with gzip.open(file_name, 'rb') as f_in:
        with open(file_name + '.txt', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return file_name + '.txt'


def parse_result(index, sorted_invert_keys):
    for entry in sorted_invert_keys:
        total_df = 0
        string = ""
        dict = index[entry]
        for docno in dict.keys():
            total_df += int(dict[docno])
            string += "\t" + docno + "," + str(dict[docno]) + "\n"
        print(total_df, "=df(", entry, ")")
        print(string)

# path = /id/a/b/c/d/.. -> id
def extract_id(path):
    return path.split("/")[1]

# path = /id/a/b/c/d/.. -> /a/b/c/d/..
def extract_path(path):
    return "/"+"/".join(path.split("/")[2:])


def get_document_length(doc_id, document_lengths=DOCUMENT_LENGTHS):
    return DOCUMENT_LENGTHS[doc_id]


def generate_index(stemmer="nostem", stop_words="nostop",elements=None, data=FILE_LIST, print_index="N"):
    '''
    :param stemmer:  "nostem" default. to enable stemmer put "porter"
    :param stop_words: "nostop" default. to enable stopwords put "stop"
    :param data: list of file to index
    :param print_index: "N" default. to print postings list put "Y"
    :return: inverted index
    '''
    if elements is None:
        elements = ["article","title","bdy","sec"]

    global path_data_list

    if path_data_list=={}:
        for document_path in FILE_LIST:
            walkTreeForElemnts(document_path,elements)

    elementsList = elements

    document_list = []

    global STOP_WORDS,_STOP_WORDS
    global STEMMER

    if stop_words != "nostop":
        STOP_WORDS = True

    if stemmer != "nostem":
        STEMMER = True

    print("---   Indexing with :", stemmer, "_", stop_words)

    #if custom stop words list indicated we change the _STOP_WORDS list accordingly
    if STOP_WORDS:
        if(stop_words_filename!=""):
          f_stop_words = open(stop_words_filename, "r", encoding='utf-8')
          stop_words = f_stop_words.read()
          stop_words = stop_word_split(stop_words)
          _STOP_WORDS = set(stop_words)

    start_time = time.time()

    # Build Inverted-Index for documents
    inverted = {}
    sorted_invert_keys = []
    documents = path_data_list
    global TIME

    for doc_id, text in documents.items():
        TIME = (time.time() - start_time)
        #print("[",TIME,"]",doc_id)
        doc_index = inverted_index(doc_id, text)
        inverted_index_add(inverted, doc_id, doc_index)

    TIME = (time.time() - start_time)
    print("---   FINISHED IN %s seconds" % (TIME))

    if (print_index == "Y"):
        # Print Inverted-Index
        sorted_invert_keys = sorted(inverted)
        parse_result(inverted, sorted_invert_keys)

    stats(inverted)

    return inverted

def term_frequency(word, document_id, inverted):
    #word = stem_word(word)
    dictionary = dict()
    if word in inverted.keys():
        dictionary = inverted[word]
        if document_id in dictionary.keys():
            return dictionary[document_id]
        else:
            return 0
    else:
        return 0


def document_frequency(word, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    #word = stem_word(word)
    tf = 0
    if word in inverted.keys():
        dictionary = inverted[word]
        return len(dictionary)
    else:
        return 0


def get_term_docs(word, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    #word = stem_word(word)
    if word in inverted.keys():
        return inverted[word].keys()
    else:
        return []


# Verified
def ltn_weighting(word, doc_id, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    global DOCUMENT_LENGTHS
    #word = stem_word(word)
    tf = term_frequency(word, doc_id, inverted)
    df = document_frequency(word, inverted)
    if tf <= 0 or df == 0:
        return 0
    return (1 + m.log10(tf)) * m.log10(len(DOCUMENT_LENGTHS) / df)


# Verified
def ltc_weighting(word, doc_id, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    global DOCUMENT_WORDS
    #word = stem_word(word)
    somme = 0
    for w in DOCUMENT_WORDS[doc_id]:
        somme += (ltn_weighting(w[0], doc_id)) ** 2
    if somme == 0:
        return 0
    else:
        return ltn_weighting(word, doc_id, inverted) / (m.sqrt(somme))


# Verified
def bm25_weighting(word, doc_id, k=K, b=B, inverted=INVERTED):
    global INVERTED, K, B
    k, b = K, B
    inverted = INVERTED
    global DOCUMENT_LENGTHS
    N = len(DOCUMENT_LENGTHS)  # nombre total de docs dans le fichier
    avdl = WORD_COUNT / N
    #word = stem_word(word)
    tf = term_frequency(word, doc_id, inverted)
    df = document_frequency(word, inverted)
    w = (tf * (k + 1)) / (k * ((1 - b) + b * (DOCUMENT_LENGTHS[doc_id] / avdl)) + tf) * m.log10((N - df + b) / (df + b))
    return w


def best_n_weights(word, n=10, func_weighting=ltn_weighting, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    #word = stem_word(word)
    weighting_list = []
    for doc_id in get_term_docs(word, inverted):
        weighting_list.append([doc_id, func_weighting(word, doc_id)])

    weighting_list = sorted(weighting_list, key=lambda x: x[1], reverse=True)
    return weighting_list[len(weighting_list) - n:]


def query_best_n_weights(query, n, func_weighting, inverted=INVERTED):
    global INVERTED
    inverted = INVERTED
    global DOCUMENT_LENGTHS
    words = query.split()
    list_best_n = []
    query_best_n = []
    for word in words:
        word = stem_word(word)
        list_best_n.append(best_n_weights(word, len(DOCUMENT_LENGTHS), func_weighting, inverted))

    set_doc_id = set()
    for best_n in list_best_n:
        for doc_weight in best_n:
            set_doc_id.add(doc_weight[0])  # 0 is docId 1 is docWeight

    for doc_id in set_doc_id:
        current_weight = 0
        for best_n in list_best_n:
            for doc_weight in best_n:
                if doc_id == doc_weight[0]:
                    current_weight += doc_weight[1]
        query_best_n.append([doc_id, current_weight])
    query_best_n = sorted(query_best_n, key=lambda x: x[1], reverse=True)
    return query_best_n[:n]


def run_algo(query_id, query, func_weighting, inverted=INVERTED):  # score should be decreasing
    global INVERTED
    inverted = INVERTED
    global DOCUMENT_LENGTHS, QUERY_RESULTS_LIMIT
    if func_weighting == "ltc":
        query_result = query_best_n_weights(query, QUERY_RESULTS_LIMIT, ltc_weighting, inverted)
    elif func_weighting == "ltn":
        query_result = query_best_n_weights(query, QUERY_RESULTS_LIMIT, ltn_weighting, inverted)
    elif func_weighting == "bm25":
        query_result = query_best_n_weights(query, QUERY_RESULTS_LIMIT, bm25_weighting, inverted)
    i = 0
    result = ""
    if not ALLOW_ENTRELACEMENT:
        query_result = removeInterleaving(query_result)
    for doc_id, score in query_result:
        i += 1
        result += str(query_id) + " Q0 " + str(extract_id(doc_id)) + " " + str(i) + " " + str(
            score) + " " + TEAM + " " + str(extract_path(doc_id)) + "\n"
    return result

def removeInterleaving(query_result):
    docummentMaxScores = {}
    oldListId = [extract_id(x) for x,y in query_result]
    oldListPath = [x for x,y in query_result]
    newList = []

    for path , score in query_result:
        docId = extract_id(path)
        if docId not in docummentMaxScores.keys():
            docummentMaxScores[docId]=score

    for docId in docummentMaxScores.keys():
        while docId in oldListId:
            i = oldListId.index(docId)
            oldListId.pop(i)
            newList.append((oldListPath.pop(i),docummentMaxScores[docId]))

    return newList

query_list = [(2009011, "olive oil health benefit"),
              (2009036, "notting hill film actors"),
              (2009067, "probabilistic models in information retrieval"),
              (2009073, "web link network analysis"),
              (2009074, "web ranking scoring algorithm"),
              (2009078, "supervised machine learning algorithm"),
              (2009085, "operating system +mutual +exclusion")]
RUN_ID = 0

def generate_query_runs(query_list, stem_nostem=None, stop_nostop=None, weighting_functions=None,
                        granularity="articles", elements=None, k_list=None, b_list=None):
    if elements is None:
        if granularity == "articles":
            elements = ["article"]
        elif granularity == "elements":
            elements = ["article", "title", "bdy", "sec"]
        else:
            elements = ["article"]
    global ALLOW_ENTRELACEMENT
    if elements is not None:
        ALLOW_ENTRELACEMENT = False
        if granularity == "articles":
            elements = ["article"]

    if b_list is None:
        b_list = [0.5, 0.75]
    if k_list is None:
        k_list = [1, 1.2]
    if weighting_functions is None:
        weighting_functions = ["ltn", "ltc", "bm25"]
    if stem_nostem is None:
        stem_nostem = ["nostem", "stem"]
    if stop_nostop is None:
        stop_nostop = ["nostop", "stop"]

    global RUN_ID, FILE_LIST, INVERTED
    global K, B
    team_name = "YahyaYasserYounesIbtissam"
    weighting_function = ""
    parameters = "k=" + str(K) + "_b=" + str(B)
    option = ""
    extended_granularity = ""
    global STEMMER
    global STOP_WORDS, _STOP_WORDS
    if STEMMER and not STOP_WORDS:
        option = "nostop_porter"
    elif not STEMMER and STOP_WORDS:
        option = "stop" + str(len(_STOP_WORDS)) + "_nostem"
    elif STEMMER and STOP_WORDS:
        option = "stop" + str(len(_STOP_WORDS)) + "_porter"
    else:
        option = "nostop-nostem"
    if granularity == "elements":
        extended_granularity = granularity + "_" + "_".join(elements)

    for stop in stop_nostop:
        option = ""
        if stop == "nostop":
            STOP_WORDS = False
            option = "nostop_"
        else:
            STOP_WORDS = True
            option = "stop" + str(len(_STOP_WORDS)) + "_"
        first_option = option
        for stem in stem_nostem:

            if stem == "nostem":
                option = first_option
                STEMMER = False
                option += "nostem"
            else:
                option = first_option
                STEMMER = True
                option += "porter"

            INVERTED = generate_index(stemmer=stem, stop_words=stop, data=FILE_LIST, print_index="N")

            for algo in weighting_functions:
                weighting_function = algo
                print("---- " + "algorithm currently used " + algo)

                if algo == "bm25":
                    for i_k in k_list:
                        K = i_k
                        for i_b in b_list:
                            B = i_b
                            parameters = "k=" + str(K) + "_b=" + str(B)
                            file_name = team_name + "_" + str(
                                RUN_ID) + "_" + weighting_function + "_" + extended_granularity + "_" + option + "_" + parameters + ".txt"
                            f = open(file_name, "w")
                            for id, query in query_list:
                                f.write(run_algo(id, query, algo, inverted=INVERTED))
                            RUN_ID += 1
                            print("---- " + file_name + " CREATED")
                            f.close()
                else:
                    parameters = ""
                    file_name = team_name + "_" + str(
                        RUN_ID) + "_" + weighting_function + "_" + extended_granularity + "_" + option + ".txt"
                    f = open(file_name, "w")
                    for id, query in query_list:
                        f.write(run_algo(id, query, algo, inverted=INVERTED))
                    RUN_ID += 1
                    print("---- " + file_name + " CREATED")
                    f.close()
    return RUN_ID

global RUN_ID
RUN_ID = generate_query_runs(query_list, stem_nostem=["nostem", "stem"], stop_nostop=["stop", "nostop"],
                             granularity="elements", weighting_functions=["ltn", "ltc"])  # 6
RUN_ID = generate_query_runs(query_list, stem_nostem=["nostem"], stop_nostop=["stop", "nostop"], granularity="elements",
                             weighting_functions=["bm25"], k_list=[1.2], b_list=arange(0, 1.1, 0.1))  #20
RUN_ID = generate_query_runs(query_list, stem_nostem=["nostem"], stop_nostop=["stop", "nostop"], granularity="elements",
                             weighting_functions=["bm25"], k_list=arange(0, 4.2, 0.2), b_list=[0.75])  #40