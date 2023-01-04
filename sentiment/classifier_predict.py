# -*- coding: utf-8 -*-

import classifier_sub
#import pandas as pd
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score,classification_report,confusion_matrix
import csv
import os
import numpy as np
import tokenizer

def label_tonum(labels):
    """ ラベル名をベクトル変換(bunruiki.predictの返却と同じnpに)"""

    labels_num = []
    for l in labels:
        if l == 'n2':
            labels_num.append(0)
        elif l == 'n1':
            labels_num.append(1)
        elif l == 'e':
            labels_num.append(2)
        elif l == 'p1':
            labels_num.append(3)
        elif l == 'p2':
            labels_num.append(4)

    return np.array(labels_num, dtype = np.uint8)               
            
def num_tolabel(num):
    """ベクトル→ラベル名変換 """
    
    labels = []
    for l in num:
        if l == int(0):
            labels.append('n2')
        elif l == int(1):
            labels.append('n1')
        elif l == int(2):
            labels.append('e')
        elif l == int(3):
            labels.append('p1')
        elif l == int(4):
            labels.append('p2')

    return labels   
            

def predict_model(num):
    """分類器精度測定
    
    num: 1 → bow
         2 → tfidf
         3 → mlp
         4 → bm25
    
    """

    
    bunruiki = classifier_sub.Myclassifier()
        
    #識別器と辞書のパス 結果書き込み字に参照
    if num == 1:
        print("predict by bow")
        calc = 'bow'
        #bow用保存ファイルパス
        filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_bow.pkl')
        filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_bow.pkl')
        #識別器と辞書読み込み
        vocab,model = bunruiki.load()  
    elif num == 2:
        print("predict by tfidf")
        calc = 'tfidf'
        #tfidf用保存ファイルパス
        filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_tfidf.pkl')
        filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_tfidf.pkl')
        #識別器と辞書読み込み
        vocab,model = bunruiki.load_tfidf()  
    elif num == 3:
        print("predict by mlp")
        calc = 'mlp'
        #mlp
        filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_mlp_bm25.pkl')
        filename_vocab2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer2_mlp_bm25.pkl')

        filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_bm25_mlp.pkl')
        #識別器と辞書読み込み
        vocab,vocab2,model = bunruiki.load_mlp()       
    elif num == 4:
        print("predict by bm25")
        calc = 'bm25'
        #mlp
        filename_vocab = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer_bm25.pkl')
        filename_vocab2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\myvectorizer2_bm25.pkl')
        
        filename_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\models\mymodel_bm25.pkl')
        #識別器と辞書読み込み
        vocab,vocab2,model = bunruiki.load_bm25()    
    else:
        return "Error! (1:bow 2:tfidf 3:mlp)"
    
#ファイルから読み込む場合-----
    #testデータ読み込み
    
    ANIMES = ['salormoon','鬼滅','sao']
    for ANIME in ANIMES:
        labels = []
        texts = []
        print("reading testdata {0}..".format(ANIME)) 
        with open("sentiment/static/sentiment/testdata/{0}_testdata.csv".format(ANIME), "r", encoding="utf_8", newline="") as f:
            for row in csv.reader(f):
                labels.append(row[0]) #取得したい列番号を指定（0始まり） 
                texts.append(row[5])
            
        del labels[0] # ヘッダー除去
        del texts[0]
        
        labels = label_tonum(labels) # ラベル名から数値(numpy)変換

        print("done.")

    #分類結果取得
        print("start predict..")
        predictions = []
        if num == 1 or num == 2:
            predictions = bunruiki.predict(texts,vocab,model) # np.int64
        elif num == 3:
            predictions = bunruiki.predict_mlp(texts,vocab,vocab2,model) # np.str_
        elif num == 4:
            predictions = bunruiki.predict_bm25(texts,vocab,vocab2,model)
        predictions = np.array(predictions, dtype = np.uint8) # 返却地が違うため統一
         
        # 出力用にTP&TNとFP&FNをそれぞれリスト化
        d_trues = []
        d_falses = []
        
        # 誤判定出力用(数値ではなくラベル名で出力させる)
        for prediction,label,text in zip(num_tolabel(predictions),num_tolabel(labels),texts):
            if label == prediction:
                d_trues.append('o:({0}→{1}) {2}\n'.format(label,prediction,text))
            else:
                d_falses.append('x:({0}→{1}) {2}\n'.format(label,prediction,text)) 
        d_trues.sort(reverse=True)
        d_falses.sort(reverse=True)
        cm = confusion_matrix(labels, predictions)
        # p→n, n→p誤判定数
        l = cm.flatten()
        n_to_p = l[3]+l[4] # n2→p1,p2
        n_to_p += l[8]+l[9] # n1→p1,p2
        p_to_n = l[15]+l[16] # p1→n1,n2
        p_to_n += l[20]+l[21] # p1→n1,n2        
        #結果をファイルに書き込み
        print("writing file..")
        with open("sentiment/static/sentiment/result/{0}_{1}_accuracy.txt".format(ANIME,calc),"w",encoding='utf-8') as f:
            f.write('used vocab:'+filename_vocab+'\n')
            f.write('used model:'+filename_model+'\n')
            f.write('ANIME:{0}\n'.format(ANIME))
            f.write('confusion matrix:\n')
            f.write(str(cm))
            f.write('n→p:'+str(n_to_p)+', p→n:'+str(p_to_n)+'\n\n')
            f.write(str(classification_report(labels,predictions,target_names=['n2','n1','e','p1','p2'])))

            f.write('\n----------不正解-------------\n')
            for d in d_falses:
                f.write(d)
            f.write('\n----------正解---------------\n')
            for d in d_trues:
                f.write(d)


            print("done.")
        
    return "Successfully done."

        
if __name__=='__main__':
   
    msg = predict_model(3) # 1:bow 2:tfidf 3:mlp
    print(msg)