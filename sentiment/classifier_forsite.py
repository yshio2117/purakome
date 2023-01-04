# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.svm import SVC
import tokenizer
import joblib

from tensorflow.keras.layers import Dense,Dropout
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import os
from bm25 import BM25Transformer


#bow用保存ファイルパス
filename_vocab_bow = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_bow.pkl')
filename_model_bow = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_bow.pkl')
#tfidf用保存ファイルパス
filename_vocab_tfidf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_tfidf.pkl')
filename_model_tfidf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_tfidf.pkl')
#bm25用保存ファイルパス
filename_vocab_bm25 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_bm25.pkl')
filename_vocab2_bm25 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer2_bm25.pkl')
filename_model_bm25 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_bm25.pkl')

#mlp用
filename_vocab_mlp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_mlp_bm25.pkl')
filename_model_mlp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_mlp_bm25.pkl')
filename_vocab2_mlp_bm25 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer2_mlp_bm25.pkl')

N_LABELS = 5 # mlp用分類クラス数
        
class Myclassifier:
    def train(self,texts: str,labels: int) -> None:
        """前処理bowで学習. 辞書と識別器の保存まで実施"""
        
        vectorizer = CountVectorizer(tokenizer=tokenizer.tokenize)
        print('--started creating bow--')
        texts = [tokenizer.cleansing_text(text) for text in texts]        
        bow = vectorizer.fit_transform(texts)
        print('--finished creating bow--')
        classifier = SVC()
        print('--started training--')
        classifier.fit(bow,labels)
        print('--finished training--')
        
        #分類器,ボキャブラリーの保存
        joblib.dump(vectorizer,filename_vocab_bow)                  
        joblib.dump(classifier,filename_model_bow)
        print('vectorizer saved:',filename_vocab_bow)
        print('classifier saved:',filename_model_bow)
            
    def train_tfidf(self,texts,labels):
        """tfidfでの学習"""
        
        vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize,ngram_range=(1,2))
        texts = [tokenizer.cleansing_text(text) for text in texts]        
        print('--started creating tfidf')
        tfidf = vectorizer.fit_transform(texts)
        print('--finished creating tfidf--')
        classifier = SVC(kernel='rbf')
        print('--started training--')
        classifier.fit(tfidf,labels)
        print('--finished training--')
        

        #分類器,ボキャブラリーの保存
        joblib.dump(vectorizer,filename_vocab_tfidf)                  
        joblib.dump(classifier,filename_model_tfidf)
        print('vectorizer saved:',filename_vocab_tfidf)
        print('classifier saved:',filename_model_tfidf)

    def train_bm25(self,texts,labels):
        """bm25での学習"""
        print('--started creating bow for bm25')
        vectorizer = CountVectorizer(tokenizer=tokenizer.tokenize)
        texts = [tokenizer.cleansing_text(text) for text in texts]
        bow = vectorizer.fit_transform(texts)
        print('--finished creating bow for bm25')
        print('--started creating bm25')
        vectorizer2 = BM25Transformer()
        vectorizer2.fit(bow)
        bm25 = vectorizer2.transform(bow)
        print('--finished creating bm25--')
        
        classifier = SVC(kernel='rbf')
        print('--started training--')
        classifier.fit(bm25,labels)
        print('--finished training--')
        

        #分類器,ボキャブラリーの保存
        joblib.dump(vectorizer,filename_vocab_bm25) 
        joblib.dump(vectorizer2,filename_vocab2_bm25)
        joblib.dump(classifier,filename_model_bm25)
        print('vectorizer saved:',filename_vocab_tfidf)
        print('classifier saved:',filename_model_tfidf)
        
    def train_mlp(self, texts: str, labels: int, layers: int) -> None:
        """識別器の学習mlp"""
        '''
        #特徴量tfidf
        vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize)
        print('--started creating tfidf')
        tfidf = vectorizer.fit_transform(texts)
        print('--finished creating tfidf--')
        '''
        print('--started creating bow for bm25')
        vectorizer = CountVectorizer(tokenizer=tokenizer.tokenize)
        texts = [tokenizer.cleansing_text(text) for text in texts]
        bow = vectorizer.fit_transform(texts)
        print('--finished creating bow for bm25')
        print('--started creating bm25')
        vectorizer2 = BM25Transformer()
        vectorizer2.fit(bow)
        bm25 = vectorizer2.transform(bow)
        
        
        feature_dim = len(vectorizer.get_feature_names())#特徴量次元数 入力層で必要

        print('feature_dim:',feature_dim)
        mlp = Sequential()
        #全3層 入力32unit 出力層3unit(n2,n1,e,p1,p2 0,1,2,3,4)
        print('layers:{0}'.format(layers))
 
        mlp.add(Dense(units=32,input_dim=feature_dim,activation='relu'))
        mlp.add(Dropout(0.5))
        mlp.add(BatchNormalization())
        mlp.add(Dense(units=32,activation='relu'))
        mlp.add(Dropout(0.5))
        mlp.add(BatchNormalization())
        #mlp.add(Dense(units=32,activation='relu'))
        mlp.add(Dense(units=N_LABELS,activation='softmax'))
        mlp.compile(loss='categorical_crossentropy',optimizer='adam')
        
        #onehot表現変換
        labels_onehot= to_categorical(labels,N_LABELS)
        
        print('--started training--')
        #mlp.fit(tfidf,labels_onehot,epochs=20)
        mlp.fit(bm25,labels_onehot,epochs=20)
#        mlp.fit(tfidf,labels_onehot,epochs=25,
#                validation_split=0.1,callbacks=[EarlyStopping(min_delta=0.0,patience=2)])
        print('--finished training--')
        
        #分類器,ボキャブラリーの保存
        joblib.dump(vectorizer,filename_vocab_mlp) 
        joblib.dump(vectorizer2,filename_vocab2_mlp_bm25)                 
        joblib.dump(mlp,filename_model_mlp)
        print('vectorizer saved:',filename_vocab_mlp)
        print('mlp saved:',filename_model_mlp)
        
    def predict(self,texts,vectorizer,classifier):
        """識別器で分類"""

        texts = [tokenizer.cleansing_text(text) for text in texts]
        bow = vectorizer.transform(texts)
        
        return classifier.predict(bow)
    
    def predict_bm25(self,texts,vectorizer,vectorizer2,classifier):
        """識別器で分類"""

        texts = [tokenizer.cleansing_text(text) for text in texts]
        bow = vectorizer.transform(texts)
        bm25 = vectorizer2.transform(bow)
        
        return classifier.predict(bm25)
    '''    
    def predict_mlp(self,texts,vectorizer,mlp):
        """識別器で分類 mlp用"""
        
        #特徴量tfidf
        tfidf = vectorizer.transform(texts)
        predictions = mlp.predict(tfidf)
        predicted_labels = np.argmax(predictions, axis=1)
        return predicted_labels
    '''
    def predict_mlp(self,texts,vectorizer,vectorizer2,mlp):
        """識別器で分類 mlp用"""
        
        #特徴量tfidf

        texts = [tokenizer.cleansing_text(text) for text in texts]
        bow = vectorizer.transform(texts)
        bm25 = vectorizer2.transform(bow)        
        predictions = mlp.predict(bm25)
        predicted_labels = np.argmax(predictions, axis=1)
        return predicted_labels
    
    def load(self) -> None:     
        """辞書と学習済み識別器の読込"""
        
        print("loading vocab:",filename_vocab_bow)
        print("loading model:",filename_model_bow)
        vectorizer = joblib.load(filename_vocab_bow)
        classifier = joblib.load(filename_model_bow)
        print("finished loading")
        return(vectorizer,classifier)

    def load_tfidf(self) -> None:     
        """辞書と学習済み識別器の読込"""
        
        print("loading vocab:",filename_vocab_tfidf)
        print("loading model:",filename_model_tfidf)
        vectorizer = joblib.load(filename_vocab_tfidf)
        classifier = joblib.load(filename_model_tfidf)
        print("finished loading")
        return(vectorizer,classifier)

    def load_mlp(self) -> None:
        """辞書と学習済み識別器の読込みfor mlp"""
        
        print("loading vocab:",filename_vocab_mlp)
        print("loading model:",filename_model_mlp)
        vectorizer = joblib.load(filename_vocab_mlp)
        vectorizer2 = joblib.load(filename_vocab2_mlp_bm25)
        classifier = joblib.load(filename_model_mlp)
        print("finished loading")
        return(vectorizer,vectorizer2,classifier)
 
    def load_bm25(self) -> None:
        """辞書と学習済み識別器の読込みfor bm25"""
        
        print("loading vocab:",filename_vocab_bm25)
        print("loading vocab2:",filename_vocab2_bm25)
        print("loading model:",filename_model_bm25)
        vectorizer = joblib.load(filename_vocab_bm25)
        vectorizer2 = joblib.load(filename_vocab2_bm25)
        classifier = joblib.load(filename_model_bm25)
        print("finished loading")
        return(vectorizer,vectorizer2,classifier)