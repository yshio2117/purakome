from django.shortcuts import render
from .dictadd import dictadd
import csv

# Create your views here.
def addword(request):
    #print('mecab')
    if request.method == "GET":
        params = {
                 'base':None,
                 'w_class':None,
                 'result':None,

                 }
    else:
        w_class = request.POST.get('group_link_radios')
        base = request.POST.get('base')
        yomi = request.POST.get('yomi')
        hitei = request.POST.get('hitei')

        if w_class == '形容詞':
            #print('形容詞')
            with open("/opt/mecab-ipadic-neologd/build/mecab-ipadic-2.7.0-20070801-neologd-20200910/Adj.csv", "r", encoding="utf_8", newline="") as f:
                reader = csv.reader(f)
                dic_l = [r for r in reader]
                #print('len:',len(dic_l))
                #print(dic_l[0])
        elif w_class == '動詞':
            #print('動詞')
            with open("/opt/mecab-ipadic-neologd/build/mecab-ipadic-2.7.0-20070801-neologd-20200910/Verb.csv", "r", encoding="utf_8", newline="") as f:
                reader = csv.reader(f)
                dic_l = [r for r in reader]   
                #print('len:',len(dic_l))

        
        result = dictadd(w_class,base,hitei,yomi,dic_l)
        #print('result:',result)
        params = {
            'base':base,
            'w_class':w_class,
            'result':result,
            }
       
    #print('param',params)
    return render(request,'mecab/addword.html',params)

