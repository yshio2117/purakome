# -*- coding: utf-8 -*-


import os

import classifier_sub
import csv
import tokenizer



def make_model(num,layers):
    """分類器作成
    
    num: 1 → bow
         2 → tfidf
         3 → mlp
    layers: int (>=2)
            (for only mlp) 
    
    """
    
    if num == 1:
        print("make by bow")
    elif num == 2:
        print("make by tfidf")
    elif num == 3:
        print("make by mlp")
    elif num == 4:
        print("make by bm25")
    else:
        return "Error! (1:bow 2:tfidf 3:mlp 4:bm25)"
    
    bunruiki = classifier_sub.Myclassifier()

    print("reading textdata..")
    #教師データ読み込み
    labels = []
    texts = []
    with open("sentiment/static/sentiment/traindata/training_label.csv", "r", encoding="utf_8", newline="") as f:
        for row in csv.reader(f):
            labels.append(row[0]) #取得したい列番号を指定（0始まり） 
            texts.append(row[1])
        
    del labels[0] # ヘッダー除去
    del texts[0]
    print("done.")
    print('labels number:',len(labels))
    print('texts number:',len(texts))
    
    if num == 1:
        bunruiki.train(texts,labels)
    elif num == 2:
        bunruiki.train_tfidf(texts,labels)
    elif num == 3:
        if layers < 2:
            return "error! layers >= 2"
        bunruiki.train_mlp(texts,labels,layers)
    elif num == 4:
        bunruiki.train_bm25(texts,labels)
    
    return "Successfully made."


if __name__=='__main__':
    path = os.getcwd()
    print(path)
    msg = make_model(3,3) # 1:bow 2:tfidf 3:mlp
    print(msg)