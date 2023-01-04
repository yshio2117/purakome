# -*- coding: utf-8 -*-

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer 

import gspread
import itertools
import re
import MeCab
import unicodedata,neologdn
import pprint

import gensim
from gensim import corpora
import os,sys
import csv

STOP_WORDS_FORSUMY=['思う','言う','殺す','死ぬ','やばい','凄い','すごい','めちゃくちゃ','めっちゃ','くる','いく',
            '来る','出る','すぎる','過ぎる','いう','泣く','する','てる',
            'なる','れる','やる','られる','の','ん','ある','さん','ちゃん','こと',
            '事','やつ','奴','日','人','僕','私','俺','あれ','これ','それ','w','笑']

STOP_WORDS=['思う','言う','くる','いく','めちゃくちゃ','めっちゃ','行く','いない','しない',
            '来る','出る','すぎる','過ぎる','いう','泣く','する','てる',
            'なる','れる','やる','られる','の','ん','ある','さん','ちゃん','こと',
            '事','やつ','奴','日','人','僕','私','俺','あれ','これ','それ','w','笑']

def gensim_classifier(documents,num_topics=5):

    '''
    # orgシートから読み込み
    worksheet = sheet.worksheet('org')
    
    documents = worksheet.col_values(1)
    documents.pop(0) # タイトル行削除    
    '''
    texts=[]
    for document in documents:
        texts.append(wakachi(document,['助詞','助動詞','記号']))
    
    dictionary = corpora.Dictionary(texts)
    # ファイルに保存できる
    #dictionary.save('/static/sentiment/deerwester.dict')
    
    #1曲のみに出現、2割以上の曲に出現する単語を削除
    dictionary.filter_extremes(no_below=2,no_above=0.8)
    
    filename_gensimdic = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\deerwester.dict.txt')
    filename_gensimcorpus = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\sentiment\deerwester.mm')
    
    # テキストファイルに保存できる
    dictionary.save_as_text(filename_gensimdic)
    
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # ファイルに保存できる
    corpora.MmCorpus.serialize(filename_gensimcorpus, corpus)
    
    # num_topics=5で、5個のトピックを持つLDAモデルを作成
    lda = gensim.models.ldamodel.LdaModel(corpus=corpus, num_topics=num_topics,\
                                          id2word=dictionary)

    #文をトピック分類    
    tpcs=[] # 各文のトピック
     # 最もスコアの高いtopicを選出
    for i in range(len(documents)):
        scores_pertext=[]
        for topics_per_document in lda[corpus[i]]:
           scores_pertext.append(topics_per_document[1])
           
        tpcs.append(scores_pertext.index(max(scores_pertext)))

    tpc_perdoc = []
    for d,t in zip(documents,tpcs):
        tpc_perdoc.append({'topic':t,'原文':d})

    classified_doc = []
    for i in range(num_topics):
        classified_doc.append([tpc['原文'] for tpc in tpc_perdoc if tpc['topic'] == i])
    
    return classified_doc


def cleansing_text(text):

    # テキスト正規化
    text = unicodedata.normalize('NFKC',text)#表記ゆれの統一
    text = neologdn.normalize(text)# アルファベット,数字,記号の全角半角統一
    text = text.lower()# 小文字化
    
    return text

    
def wakachi(text, exclude_class = ['助詞','助動詞','副詞','記号']):
    
    
    text = unicodedata.normalize('NFKC',text)
    text = neologdn.normalize(text)
    text = text.lower()
    
    tagger = MeCab.Tagger(r'-u C:\PROGRA~1\MeCab\dic\usrdic\OriginalWords.dic')
    node = tagger.parseToNode(text)
    result =[]
    while node:
        features = node.feature.split(',')
        if features[0] != 'BOS/EOS':
            if features[0] not in exclude_class:
                token = features[6] if features[6] != '*' else node.surface
                result.append(token.lower())
        node = node.next

    return result


def tokenize_subject(text,stop_words):
    
    text = cleansing_text(text)
    tagger = MeCab.Tagger(r'-u C:\PROGRA~1\MeCab\dic\usrdic\OriginalWords.dic')
    node = tagger.parseToNode(text)
    subs =[]
    verbs = []
    while node:
        features = node.feature.split(',')
        if features[0] != 'BOS/EOS':
                
            if features[6].lower() not in stop_words and node.surface.lower() not in stop_words:
                if (features[0] in ['動詞','形容詞'] and node.surface not in ['なう','最初','最後'])\
                                   or (features[0] == '名詞' and features[1] == '形容動詞語幹'):
                    token = features[6] if features[6] != '*' else node.surface                                       
                    verbs.append(token)
                elif features[0] in ['名詞'] and features[1] in ['一般','固有名詞','サ変接続']\
                                            and re.search(r"\d+[人時分秒円回]",features[6]) == None\
                                            and features[6] not in ['マジで']: #解析ミス
                    token = features[6] if features[6] != '*' else node.surface
                    subs.append(token.lower())
        node = node.next

        
    return subs, verbs
    
        

if __name__=='__main__':
    
 
    '''
    gc = gspread.service_account()
    
    # 全キャラ取得
    sh = gc.open_by_key('1b-89Ynrpek39vny4sPfkaYqNp-WYLZJ6txAjaEAld9I') # anime_keywords
    
    worksheet = sh.worksheet('all_charas')
    allchara_key = (worksheet.acell('a2').value).split(',') # salormoon
    '''
    allchara_key = ['セーラームーン','セーラーサターン','セーラージュピター','セーラーマーキュリー','セーラービーナス','セーラーヴィーナス','セーラーV','セーラーマーズ','ちびムーン','セーラーウラヌス','セーラーネプチューン','セーラープルート','月野うさぎ','プリンセス・セレニティ','水野亜美','火野レイ','地場衛','木野まこと','愛野美奈子','ちびうさ','天王はるか','海王みちる','冥王せつな','土萠ほたる','タキシード仮面','タキシードマスク','プリンス・エンディミオン','ネヘレニア','鬼滅','炭治郎','禰豆子','善逸','嘴平伊之助','栗花落カナヲ','玄弥','冨岡義勇','胡蝶しのぶ','煉獄','宇髄','無一郎','甘露寺','悲鳴嶼','伊黒','不死川','胡蝶カナエ','猗窩座','神崎アオイ','鬼舞辻','産屋敷','輝利哉','真菰','ワニ先生','鱗滝','桑島慈悟郎','中原すみ','寺内きよ','高田なほ','鉄珍','鋼鐵塚','鉄穴森','黒死牟','魘夢','槇寿郎','瑠火','千寿郎','杏寿郎','堕姫','松衛門','銀子','うこぎ','チュン太郎','獪岳','無惨','妓夫太郎','ぎゅうたろう','ソードアート','SAO','桐ヶ谷和人','キリト','結城明日奈','アスナ','ユージオ','ツーベルク','ティーゼ','ウンベール','ロニエ','フィゼル','リネル','ファナティオ','アズリカ','リーバンテイン','ソルティリーナ','ゴルゴロッソ','兎沢深澄','エギル','キバオウ','現実主義勇者','ソーマ・カズヤ','リーシア','アイーシャ・ウドガルド','ジュナ・ドーマ','ロロア・アミドニア','ハクヤ・クオンミン','ポンチョ・パナコッタ','トモエ・イヌイ','ハルバート・マグナ','カエデ・フォキシア','カストール・バルガス','カルラ・バルガス','ゲオルグ・カーマイン','アルベルト・エルフリーデン','エリシャ・エルフリーデン','ガイウス・アミドニア','異世界食堂','転生したらスライムだった件','リムル','狼王','ヴェルドラ','クロエ・オベル','井沢静江','転スラ','ベニマル','シュナ','シオン','ソウエイ','ハクロウ','クロベエ','リグルド','リグル','ゴブタ','ランガ','カイジン','ゲルド','ガビル','ソーカ','ベスター','トレイニー','ヨウム','ディアブロ','ミュウラン','智慧之王','クロエ','大賢者','プラチナエンド','進化の実','吸血鬼すぐ死ぬ','ドラルク','ヒナイチ','半田桃','フクマ','吸血鬼ロナルド','見える子ちゃん','四谷みこ','二暮堂ユリア','百合川ハナ','四谷恭介','遠野善','タケダミツエ','神童ロム','古見さん','只野仁人','半妖の夜叉姫','日暮とわ','海賊王女','フェナ','最果てのパラディン']
    
    allchara_key.append('米津玄師')
    allchara_key.append('lisa')
    allchara_key.append('マンウィズ')
    allchara_key.append('dish')
    allchara_key.append('北村拓海') # 小文字で記載必要
    allchara_key = [c.lower() for c in allchara_key]
    
    #chara_name = ['LISA'] # mecab 原形で記載必要 (lisa → LISA)
    #出力ファイルオープン
#   sh = gc.open_by_key('1__Nt5cIpateYFQUILoY-zIYOVhyzw54kJEtmKFMTNAc') # 米津
#    sh = gc.open_by_key('1zpNsvOMfwAXTyUz7Fqn7L8NeNBRgzCbjLreIjQxQXpM') # lisa
    with open("C:/Users/yusuk/dkango_app/sentiment/static/sentiment/pnreason/input.csv", "r", encoding="utf_8", newline="") as f:
        dict_reader = csv.DictReader(f, fieldnames=['原文'])  # ヘッダー名指定
        documents = [row['原文'] for row in dict_reader]

    del documents[0] # ヘッダー削除
#    documents = [d for d in documents['原文']]
    # gensimでトピック分類

    tpcs = gensim_classifier(documents)
    '''
    print('tpc0:',tpcs[0][0:5])
    print('tpc1:',tpcs[1][0:5])
    print('tpc2:',tpcs[2][0:5])
    print('tpc3:',tpcs[3][0:5])
    print('tpc4:',tpcs[4][0:5])   
    '''
    summary_pertopic = []  
    LexRankSummarizer = LexRankSummarizer()
    LexRankSummarizer.stop_words = STOP_WORDS_FORSUMY
        
    for topi in range(len(tpcs)):

        #worksheet = sh.worksheet('{0}'.format(topi))
        #documents = worksheet.col_values(1)
        #tweets = worksheet.range('a2:a279')
        
        #documents.pop(0) # タイトル行削除
        print('topic len:',len(tpcs[topi]))
    
        text = '\n'.join(tpcs[topi])
        text = text.replace("#","")
        
        p = re.compile(r'「|」|\(|\)|\[|\]|\n+|\t+|。+|!+|\?+|、+|…+|・・+')
        sentences = [t for t in p.split(text)]
        
        p2 = re.compile(r'|'.join(allchara_key))
        sentences_excludechara = [p2.sub("",s.lower()) for s in sentences] #chara名(小文字に統一)は全除去
        
        #sentences_excludechara = sentences
        
    #    sentences_excludechara = [s for s in sentences_excludechara if s not in allchara_key]
        #print(sentences)
        tokens = []
        p3 = re.compile(r'。+') # 形態素解析の結果"。"が入る場合があるので除去する
        for s in sentences_excludechara:
            tokens.append([p3.sub("",w) for w in wakachi(s,['助詞','助動詞','記号','副詞'])])
        corpus = [' '.join(token) + '。' for token in tokens]

        if len(corpus)!=len(sentences_excludechara) or len(sentences)!=len(sentences_excludechara):
            print(len(corpus))
            print(len(sentences))
            print(len(sentences_excludechara))
            print("ERROR!!!!!!!!!!!!!!!!!!")
            
        parser = PlaintextParser.from_string("".join(corpus),Tokenizer("japanese"))

        
        #Lex-Rank     
        summary = LexRankSummarizer(document=parser.document,sentences_count=5)#5行要約
        '''
        #LSA
        lsa_summarizer = LsaSummarizer()
        lsa_summarizer.stop_words = STOP_WORDS
        summary = lsa_summarizer(document=parser.document,sentences_count=10)#3行要約
        
        #TextRank
        TextRankSummarizer = TextRankSummarizer()
        TextRankSummarizer.stop_words = STOP_WORDS
        summary = TextRankSummarizer(document=parser.document,sentences_count=5)#5行要約
        '''
        
        # 要約文候補5つ取得
        summarys_pertopic = []
        for sentence in summary:
            #print(tokenizer3.tokenize(sentences[corpus.index(sentence.__str__())]))
            summarys_pertopic.append(sentences[corpus.index(sentence.__str__())])
        
        # 50字以上の要約は切り捨て
        shortsummarys_pertopic = [s for s in summarys_pertopic if len(s)<=40]
        if len(shortsummarys_pertopic) == 0:
            shortsummarys_pertopic = summarys_pertopic

        # トピック内の要約を一つだけ選ぶ    
        numchk = []
        for s in shortsummarys_pertopic:
            breakflag = False
            onlycharaname = False # キャラ名が主語の場合
            subs, verbs = tokenize_subject(s, STOP_WORDS) #キャラ名は除かず主語抽出
            #print('subs:',subs)
            if 0 < len(subs) and len(subs) < 4 and 0 < len(verbs):
                if len([c for c in allchara_key if c in subs]) > 0: # subsにキャラ名が含まれる場合
                    if set(subs).issubset(set(allchara_key)) == False: # キャラ名以外に主語があればキャラ名除外
                        subs = [s for s in subs if s not in allchara_key]
                    else:
                        onlycharaname = True
                for i in range(len(summary_pertopic)):# 主語のいずれかがすでに他のトピックにあるか検索
                    for sub in subs: 
                        if sub in summary_pertopic[i]['主語']:
                            breakflag = True
                            break
                    if breakflag == True:
                        break
                    '''
                    if set(subs).issubset(set(summary_pertopic[i]['主語'])): #すでに全主語が他のトピックで要約されている場合
                        breakflag = True    
                        break
                    '''
                if breakflag == False:
                    # 主語を含む投稿を抽出(同topicの原文の検索)
                    org = [] # 該当する投稿
                    if onlycharaname == False: # 主語のみで検索
                        for document in tpcs[topi]:
                            num = 0
                            for sub in subs:
                                # 全単語含まれる場合
                                if sub in wakachi(document):
                                    num+=1
                                if len(subs) == num: 
                                    org.append(document)
                                    break
                                '''
                                # 主語のいずれかが含まれる場合
                                if sub in wakachi(document):
                                    org.append(document)
                                    break
                                '''
                    else: # キャラ名＋述語で検索
                        for verb in verbs:  
                            org_per_v = []
                            for document in tpcs[topi]:    
                                for sub in subs:
                                    w = wakachi(document)
                                    if sub in w and verb in w:
                                        org_per_v.append(document)
                                        break    
                            org.append(org_per_v)
                        maxdocs = 0 # 投稿数の最も多い述語を選ぶ
                        o_index = 0
                        for i,o in enumerate(org):
                            if len(o) > maxdocs:
                                maxdocs = len(o)
                                o_index = i
                        org = org[o_index]
                            
                    numchk.append({'要約':s,'主語':subs,'原文':org})
        #print('numchk',numchk)
        
        # 要約が見つからない場合,要約はなし
        if len(numchk) == 0:
            summary_pertopic.append({'要約':'','主語':[],'原文':''})            
        # 投稿数の最も多い要約を選ぶ
        else:
            maxnum = 0
            d_index = 0
            for i,d in enumerate(numchk):
                if len(d['原文']) > maxnum:
                    maxnum = len(d['原文'])
                    d_index = i
            summary_pertopic.append(numchk[d_index]) 
            
    # 投稿数順に並び替え
    summary_pertopic = sorted(summary_pertopic, key=lambda x:len(x['原文']),reverse = True)       
    pprint.pprint(summary_pertopic)