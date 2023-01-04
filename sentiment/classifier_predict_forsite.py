# -*- coding: utf-8 -*-

from classifier import Myclassifier
import pandas as pd
from sklearn.metrics import accuracy_score,precision_score,recall_score,classification_report


bunruiki = Myclassifier()

vocab,model = bunruiki.load()

'''
#ファイルから読み込む場合-----
test_data = pd.read_table('static/sentiment/test.csv')

predictions=[]
predictions = bunruiki.predict(test_data['text'],vocab,model)

print('predi:',predictions)

trues=[]
for c in test_data['label']:
    trues.append(c)
print('trues:',trues)
print("1:",trues.count(1))
print("0:",trues.count(0))
print("-1:",trues.count(-1))

print('accuracy:',accuracy_score(trues,predictions))
print('recall:',recall_score(trues,predictions,average=None,zero_division=0))
print('precision:',precision_score(trues,predictions,average=None,zero_division=0))
#------------------


'''
#while True:
#    print('enter text:')
def label_get(input_text):
    predictions = bunruiki.predict([input_text],vocab,model)
    return(predictions[0])
'''
    if predictions[0]==1:
        print('Positive\n')
    elif predictions[0]==0:
        print('Neutral\n')
    elif predictions[0]==-1:
        print('Negative\n')
'''