from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

import tensorflow as tf
import cv2
import numpy as np
# import matplotlib.pyplot as plt
# from tensorflow.keras.models import load_model

# fuctions import 
from functions import *

import re
from nltk.tokenize import word_tokenize
from string import punctuation 
import nltk
from nltk.corpus import stopwords
from nltk import punkt
import random as r

import pymysql
conn = pymysql.connect(host="localhost",user="root",passwd="",db="fake_feedback")
print('Database Connected ...')
cur = conn.cursor()

try:
    d = "select * from reviews"
    cur.execute(d)
    review_data = cur.fetchall()
    neg = "select * from negative_words"
    cur.execute(neg)
    neg_words = cur.fetchall()
except Exception as e:
    print("ERROR=",e)
    
review = []
ip_addr = []
negatives = []
db = []

for i in review_data:
    ip_addr.append(i[1])

for i in neg_words:
    negatives.append(i[1])
    
db.append(ip_addr)
db.append(negatives)

verify = ['Multiple reviews from same IP','Too many Negative Words','Self Promotion','Promotions via Links']
    
    
# Define a flask app
app = Flask(__name__)

# Model saved with Keras model.save()
import pickle
f = open('models/ReviewClassifier', 'rb')
model = pickle.load(f)
f.close()

result = ""

print('Model loaded. Start serving...')

print('Model loaded. Check http://127.0.0.1:5000/')


@app.route('/', methods=['GET'])
def index():   
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        
        r_ip = request.form['review']
        
        ip_ip = request.form.get("ipaddr")
        
        if ip_ip == None:
            ipr = r.choice(ip_addr)
        else:
            ipr = ip_generator()

        answer = review_detection(r_ip,ipr,model,db)
        # # 
        if answer == -1:
            e = "ERROR"
        else:
            
            ans_s = answer[1]
            ans_f = answer[0]
            reasons = answer[2] 
            Mul = reasons[0]
            Neg = reasons[1]
            Self = reasons[2]
            Link = reasons[3]
                  
            if ans_s == "NEGATIVE":
                S_color = 'RED'
            else:
                S_color = 'GREEN'
    
        r_ip = request.form['review']
        return render_template('index.html',Sentiment = ans_s,Fake=ans_f,Mul = Mul,Neg = Neg,Self = Self,Link = Link,S_color=S_color,review = r_ip)
    return None

if __name__ == '__main__':
    # app.run(port=5002, debug=True)

    # Serve the app with gevent
    http_server = WSGIServer(('0.0.0.0',5000),app)
    http_server.serve_forever()
