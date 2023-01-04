# -*- coding: utf-8 -*-

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer 

import re
import MeCab
import unicodedata,neologdn
import pprint

import gensim
from gensim import corpora
import copy

STOP_WORDS_FORSUMY=['思う','言う','殺す','死ぬ','やばい','凄い','すごい','めちゃくちゃ','めっちゃ','くる','いく',
            '来る','出る','すぎる','過ぎる','いう','泣く','する','てる','見る','みる',
            'なる','れる','やる','られる','の','ん','ある','さん','ちゃん','こと',
            '事','やつ','奴','日','人','僕','私','俺','あれ','これ','それ','w','笑']

STOP_WORDS=['思う','言う','くる','いく','めちゃくちゃ','めっちゃ','行く','いない','しない','見る','みる','観る',
            '来る','出る','すぎる','過ぎる','いう','する','てる','いる','できる',
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

    #1曲のみに出現、2割以上の曲に出現する単語を削除
    dictionary.filter_extremes(no_below=2,no_above=0.8)

    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # num_topics=5で、5個のトピックを持つLDAモデルを作成
    
    try:
        lda = gensim.models.ldamodel.LdaModel(corpus=corpus, num_topics=num_topics,\
                                          id2word=dictionary)
    except ValueError as e:
        print(e)
        return ''
    except ZeroDivisionError as e2:
        print(e2)
        return ''
        

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
    
    tagger = MeCab.Tagger()
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
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    subs =[]
    verbs = []
    while node:
        features = node.feature.split(',')
        if features[0] != 'BOS/EOS':
                
            if features[6].lower() not in stop_words and node.surface.lower() not in stop_words:
                if (features[0] in ['動詞','形容詞'] and node.surface not in ['なう','最初','最後','まじ']\
                                   and features[1] == '自立')\
                                   or (features[0] == '名詞' and features[1] == '形容動詞語幹'):
                    token = features[6] if features[6] != '*' else node.surface                                       
                    verbs.append(token)
                elif features[0] in ['名詞'] and features[1] in ['一般','固有名詞','サ変接続']\
                                            and re.search(r"\d+[人時分秒円回歳才]",features[6]) == None\
                                            and features[6] not in ['ww','www','マジで','子','人','奴','やつ']: #解析ミス
                    token = features[6] if features[6] != '*' else node.surface
                    subs.append(token.lower())
        node = node.next

        
    return list(set(subs)), list(set(verbs))
    

def take_summary(allchara_key, document_ids, maxlength=50, num_topics=5, num_summary=5):
    """
    

    Parameters
    ----------
    chara_name : list
        対象キャラ名をmecab原形で入れる (ex LISA)
    documents : list
        タプル(解析する文章,t_id)のリスト
    maxlength : int, optional
        要約文の最大文字数. The default is 50.
    num_topics :int, optional
        topic数. The default is 5.
    num_summary : int, optional
        要約文数. The default is 5.

    Returns
    -------
    summary_pertopic : dict
        

    """
    
    document_ids = copy.copy(document_ids) #関数内要素を削除するのでコピーしておく
    documents = [d[0] for d in document_ids]
    
    #allchara_key = ['セーラームーン','セーラーサターン','セーラージュピター','セーラーマーキュリー','セーラービーナス','セーラーヴィーナス','セーラーV','セーラーマーズ','ちびムーン','セーラーウラヌス','セーラーネプチューン','セーラープルート','月野うさぎ','プリンセス・セレニティ','水野亜美','火野レイ','地場衛','木野まこと','愛野美奈子','ちびうさ','天王はるか','海王みちる','冥王せつな','土萠ほたる','タキシード仮面','タキシードマスク','プリンス・エンディミオン','ネヘレニア','鬼滅','炭治郎','禰豆子','善逸','嘴平伊之助','栗花落カナヲ','玄弥','冨岡義勇','胡蝶しのぶ','煉獄','宇髄','無一郎','甘露寺','悲鳴嶼','伊黒','不死川','胡蝶カナエ','猗窩座','神崎アオイ','鬼舞辻','産屋敷','輝利哉','真菰','ワニ先生','鱗滝','桑島慈悟郎','中原すみ','寺内きよ','高田なほ','鉄珍','鋼鐵塚','鉄穴森','黒死牟','魘夢','槇寿郎','瑠火','千寿郎','杏寿郎','堕姫','松衛門','銀子','うこぎ','チュン太郎','獪岳','無惨','妓夫太郎','ぎゅうたろう','ソードアート','SAO','桐ヶ谷和人','キリト','結城明日奈','アスナ','ユージオ','ツーベルク','ティーゼ','ウンベール','ロニエ','フィゼル','リネル','ファナティオ','アズリカ','リーバンテイン','ソルティリーナ','ゴルゴロッソ','兎沢深澄','エギル','キバオウ','現実主義勇者','ソーマ・カズヤ','リーシア','アイーシャ・ウドガルド','ジュナ・ドーマ','ロロア・アミドニア','ハクヤ・クオンミン','ポンチョ・パナコッタ','トモエ・イヌイ','ハルバート・マグナ','カエデ・フォキシア','カストール・バルガス','カルラ・バルガス','ゲオルグ・カーマイン','アルベルト・エルフリーデン','エリシャ・エルフリーデン','ガイウス・アミドニア','異世界食堂','転生したらスライムだった件','リムル','狼王','ヴェルドラ','クロエ・オベル','井沢静江','転スラ','ベニマル','シュナ','シオン','ソウエイ','ハクロウ','クロベエ','リグルド','リグル','ゴブタ','ランガ','カイジン','ゲルド','ガビル','ソーカ','ベスター','トレイニー','ヨウム','ディアブロ','ミュウラン','智慧之王','クロエ','大賢者','プラチナエンド','進化の実','吸血鬼すぐ死ぬ','ドラルク','ヒナイチ','半田桃','フクマ','吸血鬼ロナルド','見える子ちゃん','四谷みこ','二暮堂ユリア','百合川ハナ','四谷恭介','遠野善','タケダミツエ','神童ロム','古見さん','只野仁人','半妖の夜叉姫','日暮とわ','海賊王女','フェナ','最果てのパラディン','ありふれた職業で世界最強','南雲ハジメ','シア・ハウリア','ティオ・クラルス','白崎香織','八重樫雫','畑山愛子','坂上龍太郎','檜山大介','中村恵里','谷口鈴','園部優花','玉井淳史','宮崎奈々','菅原妙子','清水幸利','遠藤浩介','オスカー・オルクス','ミレディ・ライセン','その着せ替え人形は恋をする','着せ恋','五条新菜','喜多川海夢','乾紗寿叶','乾心寿','菅谷乃羽','伊之助','ロナルド']

    #allchara_key = [c.lower() for c in allchara_key]
    
    # gensimでトピック分類
    tpcs = gensim_classifier(documents,num_topics)
    #print('tpcs:',tpcs[0][0:10])
    summary_pertopic = []  
    numchk = []
    
    LexSummarizer = LexRankSummarizer()
    LexSummarizer.stop_words = STOP_WORDS_FORSUMY
        
    for topi in range(len(tpcs)):


        print('topic len:',len(tpcs[topi]))
        num_summary = round(len(tpcs[topi])/10)
        
        text = '\n'.join(tpcs[topi])
        text = text.replace("#","")
        
        p = re.compile(r'「|」|\(|\)|\[|\]|\s+|。+|!+|！+|\?+|\？+|、+|…+|・・+')
        sentences = [t for t in p.split(text)]
    
        p2 = re.compile(r'|'.join(allchara_key))
        sentences_excludechara = [p2.sub("",s.lower()) for s in sentences] #chara名(小文字に統一)は全除去
        
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
        print("summaryizing..")
        #Lex-Rank     
        summary = LexSummarizer(document=parser.document,sentences_count=num_summary)#5行要約
        '''
        #LSA
        lsa_summarizer = LsaSummarizer()
        lsa_summarizer.stop_words = STOP_WORDS
        summary = lsa_summarizer(document=parser.document,sentences_count=num_summary)#3行要約
        
        #TextRank
        TextRankSummarizer = TextRankSummarizer()
        TextRankSummarizer.stop_words = STOP_WORDS
        summary = TextRankSummarizer(document=parser.document,sentences_count=num_summary)#5行要約
        '''
        print('done.')
        # 要約文候補5つ取得
        summarys_pertopic = []
        for sentence in summary:
            summarys_pertopic.append(sentences[corpus.index(sentence.__str__())])
        '''
        for s in summarys_pertopic:
            print('orgsummary:',s)
        '''
        # maxlength字以上の要約は切り捨て
        shortsummarys_pertopic = [s for s in summarys_pertopic if len(s)<=maxlength]
        if len(shortsummarys_pertopic) == 0:
            shortsummarys_pertopic = summarys_pertopic

        # トピック内の要約を一つだけ選ぶ    
        #numchk = []
        for s in shortsummarys_pertopic:
            breakflag = False
            subs, verbs = tokenize_subject(s, STOP_WORDS) #キャラ名は除かず主語抽出
            verbs = [v for v in verbs if v not in allchara_key] # 無惨等、キャラ名が述語になる場合を除く
            #print('shortsummary:',s,end=",")
            #print('subs;',subs,end=",")
            #print('verbs:',verbs,end=",")
            #print('subs:',subs)
            if 0 < len(subs) and 0 < len(verbs):

                for i in range(len(numchk)):
                    # 完全一致した主語の場合検索しない
                    if sorted(subs) == sorted(numchk[i]['主語']):
                        breakflag = True    
                        break
                    
                if breakflag == False:
                    # 主語を含む投稿を抽出(同topicの原文の検索)
                    org = [] # 該当する投稿
                    
                    # 全主語・全述語が含まれる投稿を検索
                    for doc_id in document_ids:
                        w = wakachi(doc_id[0],['助詞','助動詞','記号','副詞'])
                        num_s = 0
                        esc = False
                        for sub in subs:
                            if sub in w:
                                num_s += 1
                            if num_s >= 2*len(subs)/3:
                                num_v = 0
                                for verb in verbs:
                                    if verb in w:
                                        num_v += 1
                                    if num_v >= len(verbs)/2:
                                        org.append(doc_id)
                                        esc = True
                                        break
                            if esc == True:
                                break
    
                    #print('org:',len(org))
                    if len(org) >= 2:
                        numchk.append({'要約':s,'投稿数':len(org),'主語':subs,'原文':org})
                        document_ids = [d for d in document_ids if d not in org] # グルーピングされた投稿は以後カウントしない
                        #print('len(documents_ids):',len(document_ids))

        #print('numchk',numchk)
        
            
    # 投稿数順に並び替え
    summary_pertopic = sorted(numchk, key=lambda x:len(x['原文']),reverse = True)

    #pprint.pprint(summary_pertopic[topi])
   
    return summary_pertopic