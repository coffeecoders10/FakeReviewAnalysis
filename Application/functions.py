import random as r
import re
from nltk.tokenize import word_tokenize
from string import punctuation 
import nltk
from nltk.corpus import stopwords
from nltk import punkt


class PreProcessReviews:
    def __init__(self):
        self._stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])
        
    def processReviews(self, list_of_reviews):
        processedReviews=[]
            
        for review in list_of_reviews:
            processedReviews.append((self._processReview(review["text"]),review["sentiment"]))
        return processedReviews
    
    def _processReview(self, review):
        review = review.lower() # convert text to lower-case
        review = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', review) # remove URLs
        review = re.sub('@[^\s]+', 'AT_USER', review) # remove usernames
        review = re.sub(r'#([^\s]+)', r'\1', review) # remove the # in #hashtag
        review = word_tokenize(review) # remove repeated characters (helloooooooo into hello)
        return [word for word in review if word not in self._stopwords]
# preprocessedTrainingSet = reviewProcessor.processReviews(train_data)

def buildVocabulary(preprocessedTrainingData):
    all_words = []    
    for (words, sentiment) in preprocessedTrainingData:
        all_words.extend(words)
    wordlist = nltk.FreqDist(all_words)
    word_features = wordlist.keys()
    return word_features
    
def extract_features(review):
    review_words = set(review)
    f = open("wordfeatures.txt", "r")
    x = f.readlines()
    word_features = [i[:-1] for i in x]
    # word_features = buildVocabulary(preprocessedTrainingSet)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in review_words)
    return features


# trainingFeatures = nltk.classify.apply_features(extract_features, preprocessedTrainingSet)

def remove_punc(s):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    
    no_punct = ""
    for char in s:
        if char not in punctuations:
            no_punct = no_punct + char
    return no_punct
    
def verify_fake(ip,r,db):
    v = [0 for i in range(4)]
    r1 = remove_punc(r)
    rev1 = r1.split(" ")
    rev = [i.lower() for i in rev1]
    nc = 0
    myc = 0
    linkc = 0
    me_list = ['i','me','myself','my','mine','us','we','our']
    ln = ['.com','.org','.net','.gov']
    
    ipc = db[0].count(ip)
    for i in db[1]:
        nc = nc + rev.count(i)
    myc = 0
    for i in me_list:
        myc = myc + rev.count(i)
    for i in r.split(" "):
        for j in ln:
            if j in i:
                linkc = linkc + 1
    if ipc > 1:
        v[0] = 1
    if nc > 3:
        v[1] = 1
    if myc > 4:
        v[2] = 1
    if linkc > 0:
        v[3] = 1

    return v   
    
def ip_generator():
    num = [i for i in range(255)]
    ip = str(r.choice(num))+"."+str(r.choice(num))+"."+str(r.choice(num))+"."+str(r.choice(num))
    return ip
    
def review_detection(r_ip,ipr,model,db):
    verify = ['Multiple reviews from same IP','Too many Negative Words','Self Promotion','Promotions via Links']
    result = ['','']
    fake_reasons = []
    
    if ipr == -1:
        return -1

    v = verify_fake(ipr,r_ip,db)
    if v.count(1)>=3:
        result[0] = 'FAKE'
    else:
        result[0] = 'NOT FAKE'
    # for i in range(4):
    #     if v[i] == 1:
    #         fake_reasons.append(verify[i])
    
    reviewProcessor = PreProcessReviews()
    preprocessedReview = reviewProcessor._processReview(r_ip)
    NB = model.classify(extract_features(preprocessedReview))
    
    if NB == 'T':
        result[1] = 'POSITIVE'
    elif NB == 'F':
        result[1] = 'NEGATIVE'
    else:
        result[1] = 'UNDEFINED'
    
    result.append(v)
    
    return result
    
