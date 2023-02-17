# -*- coding: utf-8 -*-

import gspread
import pprint
import csv

def hiraTokata(text):
    """ 平仮名をカタカナに変換"""
    
    # textに平仮名が含まれれば文字コードに変換(ord()),対応するカタカナを検索
    ## カタカナ(chr(12449)~chr(12535)), 対応→平仮名(chr(12353,12448)
    return ''.join([chr(n+96) if (12352 < n and n < 12439)
                              else chr(n) for n in [ord(c) for c in text]])


def costcalc(yomi, katsuyou, dic):
    """仮のID,コスト算出"""
    

    l_ids=[]
    r_ids=[]
    costs=[]
    copyflag=False
    # 同読み仮名が登録にある場合 その単語からID,コスト引用    
    for d in dic:
        if d[9] != '基本形' and copyflag == False:
            continue
        elif d[11] == hiraTokata(yomi):
            copyflag=True
            l_ids.append(d[1])
            r_ids.append(d[2])
            costs.append(d[3])   
            continue
        if copyflag == True: # 同単語の全活用ID,コストコピー
            if d[9] != '基本形':                
                l_ids.append(d[1])
                r_ids.append(d[2])
                costs.append(d[3])
            else:
                break
    #print('l ids',l_ids)
    # 同読み仮名が登録に無い場合 同活用形の単語から引用
    if len(l_ids) == 0:
        copyflag=False
        for d in dic:
            if d[8] == katsuyou:
                copyflag=True
                l_ids.append(d[1])
                r_ids.append(d[2])
                costs.append(d[3])
                continue
            if copyflag == True: 
                if d[9] != '基本形':                
                    l_ids.append(d[1])
                    r_ids.append(d[2])
                    costs.append(d[3])
                else: # 次の基本形になるまでコピー
                    break     
                
    # 同活用形もない場合0で初期化
    if len(l_ids) == 0:
        l_ids = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        r_ids = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        costs = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            

    return l_ids,r_ids,costs

            
def gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana):
    """登録する単語の全エントリー作成"""
    
    entries = []
    for l_id,r_id,cost,(k,v),yomi in zip(l_ids,r_ids,costs,katsuyou2.items(),yomi_kana.values()):
        entries.append({'表層形':v,
                       '左文脈ID':int(l_id),
                       '右文脈ID':int(r_id),
                       '生起コスト':int(cost),
                       '品詞':w_class,
                       '品詞細分類1':'自立', # すべて自立で登録
                       '品詞細分類2':'*',
                       '品詞細分類3':'*',
                       '活用型':katsuyou1,
                       '活用形':k if k not in ['連用テ接続2','連用ゴザイ接続2','未然ウ接続2'] else k[:-1], # 仮の活用名であれば元に戻す
                       '原形':basicform,
                       '読み':hiraTokata(yomi),
                       '発音':hiraTokata(yomi) # 発音は登録しない
                       })  
        
    return entries

                
def dictadd(w_class,basicform,denyform="",yomi="",dic=[]):
    """mecabユーザー辞書自動追加"""

    
    # 重複登録チェック
    dup = [(i+2,d) for i,d in enumerate(dic) if d[9] == '基本形' 
                                               and d[10] == basicform]
    if len(dup) > 0:
        #print("登録済み:{0}行目".format(dup[0][0]))
        #return dup[0][1]
        return 0
    
    entries=[]
    
    if w_class == '形容詞':

        if basicform[-1] != 'い':
            return 2
        
        i_gyou = ['い','き','し','ち','に','ひ','み','り','ぎ','じ','ぢ','び','ぴ','ぃ']
        a_gyou = ['あ','か','さ','た','な','は','ま','わ','ら','が','ざ','だ','ば','ぱ','ゃ']
        u_gyou = ['う','く','す','つ','ぬ','ふ','む','ゆ','る','ぐ','ず','づ','ぶ','ぷ','ゅ']
        o_gyou = ['お','こ','そ','と','の','ほ','も','よ','ろ','を','ご','ぞ','ど','ぼ','ぽ','ょ']
        
        gokan = basicform[:-1]
        gokan_kana = yomi[:-1]
        if yomi[-2:-1] in i_gyou:
            katsuyou1 = '形容詞・イ段'
            katsuyou2 = { 
             '基本形':basicform,
             '文語基本形':gokan, #アウオ段との違い
             '未然ヌ接続':gokan + 'から',
             '未然ウ接続':gokan + 'かろ',
             '連用タ接続':gokan + 'かっ',
             '連用テ接続':gokan + 'く',
             '連用テ接続2':gokan + 'くっ',
             '連用ゴザイ接続':gokan + 'ゅう',  #アウオ段との違い
             '連用ゴザイ接続2':gokan + 'ゅぅ', #アウオ段との違い
             '体言接続':gokan + 'き',
             '仮定形':gokan + 'けれ',
             '命令ｅ':gokan + 'かれ',
             '仮定縮約１':gokan + 'けりゃ',
             '仮定縮約２':gokan + 'きゃ',
             'ガル接続':gokan
             }
            yomi_kana = {
             '基本形':yomi,
             '文語基本形':gokan_kana, #アウオ段との違い
             '未然ヌ接続':gokan_kana + 'から',
             '未然ウ接続':gokan_kana + 'かろ',
             '連用タ接続':gokan_kana + 'かっ',
             '連用テ接続':gokan_kana + 'く',
             '連用テ接続2':gokan_kana + 'くっ',
             '連用ゴザイ接続':gokan_kana + 'ゅう',  #アウオ段との違い
             '連用ゴザイ接続2':gokan_kana + 'ゅぅ', #アウオ段との違い
             '体言接続':gokan_kana + 'き',
             '仮定形':gokan_kana + 'けれ',
             '命令ｅ':gokan_kana + 'かれ',
             '仮定縮約１':gokan_kana + 'けりゃ',
             '仮定縮約２':gokan_kana + 'きゃ',
             'ガル接続':gokan_kana
             }
            # ID,コスト取得
            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
            
            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)             
                
        elif yomi[-2:-1] in a_gyou + u_gyou + o_gyou:
            katsuyou1 = '形容詞・アウオ段'
            katsuyou2 = {
             '基本形':basicform,
             '文語基本形':gokan + 'し', #アウオ段との違い
             '未然ヌ接続':gokan + 'から',
             '未然ウ接続':gokan + 'かろ',
             '連用タ接続':gokan + 'かっ',
             '連用テ接続':gokan + 'く',
             '連用テ接続2':gokan + 'くっ',
             '連用ゴザイ接続':gokan + 'う',  #アウオ段との違い
             '連用ゴザイ接続2':gokan + 'ぅ', #アウオ段との違い
             '体言接続':gokan + 'き',
             '仮定形':gokan + 'けれ',
             '命令ｅ':gokan + 'かれ',
             '仮定縮約１':gokan + 'けりゃ',
             '仮定縮約２':gokan + 'きゃ',
             'ガル接続':gokan
             }     
            yomi_kana = {
             '基本形':yomi,
             '文語基本形':gokan_kana + 'し', #アウオ段との違い
             '未然ヌ接続':gokan_kana + 'から',
             '未然ウ接続':gokan_kana + 'かろ',
             '連用タ接続':gokan_kana + 'かっ',
             '連用テ接続':gokan_kana + 'く',
             '連用テ接続2':gokan_kana + 'くっ',
             '連用ゴザイ接続':gokan_kana + 'う',  #アウオ段との違い
             '連用ゴザイ接続2':gokan_kana + 'ぅ', #アウオ段との違い
             '体言接続':gokan_kana + 'き',
             '仮定形':gokan_kana + 'けれ',
             '命令ｅ':gokan_kana + 'かれ',
             '仮定縮約１':gokan_kana + 'けりゃ',
             '仮定縮約２':gokan_kana + 'きゃ',
             'ガル接続':gokan_kana
             }
            # ID,コスト取得
            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
            
            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)       
            
        else:
            return 3
        
 

                
    elif w_class == '動詞':

        if basicform[-1] not in ['う','く','ぐ','す','つ','ぬ','ぶ','む','る']:
            return 1
        if denyform[-1] != "ず":
            return 4
        katsuyou1 = '' # 活用型
        katsuyou2 = '' # 活用形
        a_gyou = ['か','が','さ','た','な','ば','ま','ら','わ']
        a_gyou_katakana = [{'katakana':'カ','gobi':['か','き','く','け','こ','きゃ']},
                           {'katakana':'ガ','gobi':['が','ぎ','ぐ','げ','ご','ぎゃ']},
                           {'katakana':'サ','gobi':['さ','し','す','せ','そ','しゃ']},
                           {'katakana':'タ','gobi':['た','ち','つ','て','と','ちゃ']},
                           {'katakana':'ナ','gobi':['な','に','ぬ','ね','の','にゃ']},
                           {'katakana':'バ','gobi':['ば','び','ぶ','べ','ぼ','びゃ']},
                           {'katakana':'マ','gobi':['ま','み','む','め','も','みゃ']},
                           {'katakana':'ラ','gobi':['ら','り','る','れ','ろ','りゃ']},
                           {'katakana':'ワ','gobi':['わ','い','う','え','お']} # ワ行に仮定縮約はなし
                           ]


    
        if basicform[-2:] == 'する': 
            gokan = basicform[:-2]
            gokan_kana = yomi[:-2]
            katsuyou1 = 'サ変・−スル'
            katsuyou2 = {'基本形':basicform,'文語基本形':gokan + 'す',
                         '未然形':gokan + 'し','未然ウ接続':gokan + 'しよ',
                         '未然ウ接続2':gokan + 'しょ','未然レル接続':gokan + 'せ', #サ変は未然ウ接続が２つあり、辞書重複登録できないので2つめを"未然ウ接続2"とする
                         '仮定形':gokan + 'すれ','命令ｙｏ':gokan + 'せよ',
                         '命令ｒｏ':gokan + 'しろ','仮定縮約1':gokan + 'すりゃ'}
            yomi_kana = {'基本形':yomi,'文語基本形':gokan_kana + 'す',
                         '未然形':gokan_kana + 'し','未然ウ接続':gokan_kana + 'しよ',
                         '未然ウ接続2':gokan_kana + 'しょ','未然レル接続':gokan_kana + 'せ', #サ変は未然ウ接続が２つあり、辞書重複登録できないので2つめを"未然ウ接続2"とする
                         '仮定形':gokan_kana + 'すれ','命令ｙｏ':gokan_kana + 'せよ',
                         '命令ｒｏ':gokan_kana + 'しろ','仮定縮約1':gokan_kana + 'すりゃ'}
            # ID,コスト取得
            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
            
            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)
        
        #サ変動詞(ex.重んずる)        
        elif basicform[-2:] == 'ずる': 
            gokan = basicform[:-2]
            gokan_kana = yomi[:-2]
            katsuyou1 = 'サ変・−ズル'
            katsuyou2 = {'基本形':basicform,'文語基本形':gokan + 'ず',
                         '未然形':gokan + 'ぜ','未然ウ接続':gokan + 'ぜよ',
                         '仮定形':gokan + 'ずれ','命令ｙｏ':gokan + 'ぜよ',
                         '仮定縮約1':gokan + 'ずりゃ'}
            yomi_kana = {'基本形':yomi,'文語基本形':gokan_kana + 'ず',
                         '未然形':gokan_kana + 'ぜ','未然ウ接続':gokan_kana + 'ぜよ',
                         '仮定形':gokan_kana + 'ずれ','命令ｙｏ':gokan_kana + 'ぜよ',
                         '仮定縮約1':gokan_kana + 'ずりゃ'}            
            # ID,コスト取得
            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
            
            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)
        
        #五段活用・一段活用
        else:  
         
            gokan = basicform[:-1]# 一段・食べ,見,　五段・歩,ある
            gokan_kana = yomi[:-1]
            gobi_deny = denyform[-2:-1] # べ,見, 五段:か,か
                
            if len(basicform) < len(denyform): # 五段
                katsuyou = a_gyou_katakana[a_gyou.index(gobi_deny)]
                katsuyou_line = katsuyou['katakana']
                katsuyou1 = '五段・' + katsuyou_line + '行'
                
                if katsuyou_line == 'サ': #サ行のみ音便変化なし
                    katsuyou2 = {'基本形':basicform,
                                 '未然形':gokan + katsuyou['gobi'][0],
                                 '未然ウ接続':gokan + katsuyou['gobi'][4],
                                 '連用形':gokan + katsuyou['gobi'][1],
                                 '仮定形':gokan + katsuyou['gobi'][3],
                                 '命令ｅ':gokan + katsuyou['gobi'][3],
                                 '仮定縮約1':gokan + katsuyou['gobi'][5]
                                 }
                    yomi_kana = {'基本形':yomi,
                                 '未然形':gokan_kana + katsuyou['gobi'][0],
                                 '未然ウ接続':gokan_kana + katsuyou['gobi'][4],
                                 '連用形':gokan_kana + katsuyou['gobi'][1],
                                 '仮定形':gokan_kana + katsuyou['gobi'][3],
                                 '命令ｅ':gokan_kana + katsuyou['gobi'][3],
                                 '仮定縮約1':gokan_kana + katsuyou['gobi'][5]
                                 }    
                    # ID,コスト取得
                    l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
                    # 全エントリー行作成
                    entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)                    
                else:
                    # 'ラ'行のみ体言接続特殊,未然特殊が加わる
                    if katsuyou_line == 'ラ':
                        
                        mizen_sp = 'ん' # 未然特殊
                        renyou_ta = 'っ'
                        # ラ行特殊
                        if (basicform[-6:] == 'いらっしゃる' or 
                           basicform[-5:] in ['おっしゃる','らっしゃる'] or
                           basicform[-4:] == 'くださる' or
                           basicform[-3:] in ['下さる','なさる','御座る','ござる','仰言う']):
                            
                            katsuyou1 += '特殊'
                                
                            katsuyou2 = {'基本形':basicform,
                                         '未然形':gokan + katsuyou['gobi'][0],
                                         '未然特殊':gokan + mizen_sp,
                                         '未然ウ接続':gokan + katsuyou['gobi'][4],
                                         '連用形':gokan + 'い', # 理由不明.mecabに合わせる (ex.o:ください x:くださり)
                                         '連用タ接続':gokan + renyou_ta,
                                         '仮定形':gokan + katsuyou['gobi'][3],
                                         '命令ｅ':gokan + katsuyou['gobi'][3],
                                         '命令ｉ':gokan + 'い', # ラ行特殊のみ
                                         '仮定縮約1':gokan + katsuyou['gobi'][5],
                                         }
                            yomi_kana = {'基本形':yomi,
                                         '未然形':gokan_kana + katsuyou['gobi'][0],
                                         '未然特殊':gokan_kana + mizen_sp,
                                         '未然ウ接続':gokan_kana + katsuyou['gobi'][4],
                                         '連用形':gokan_kana + 'い', # 理由不明.mecabに合わせる (ex.o:ください x:くださり)
                                         '連用タ接続':gokan_kana + renyou_ta,
                                         '仮定形':gokan_kana + katsuyou['gobi'][3],
                                         '命令ｅ':gokan_kana + katsuyou['gobi'][3],
                                         '命令ｉ':gokan_kana + 'い', # ラ行特殊のみ
                                         '仮定縮約1':gokan_kana + katsuyou['gobi'][5],
                                         }   
                            # ID,コスト取得
                            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
                            
                            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)                          
                        else:
                            taigen_sp = 'ん'
                        
                            katsuyou2 = {'基本形':basicform,
                                         '未然形':gokan + katsuyou['gobi'][0],
                                         '未然特殊':gokan + mizen_sp,
                                         '未然ウ接続':gokan + katsuyou['gobi'][4],
                                         '連用形':gokan + katsuyou['gobi'][1],
                                         '連用タ接続':gokan + renyou_ta,
                                         '仮定形':gokan + katsuyou['gobi'][3],
                                         '命令ｅ':gokan + katsuyou['gobi'][3],
                                         '仮定縮約1':gokan + katsuyou['gobi'][5],
                                         '体言接続特殊':gokan + taigen_sp,
                                         '体言接続特殊2':(gokan + taigen_sp)[:-1] # 体言接続から語尾'ん'欠落したもの
                                         }
                            yomi_kana = {'基本形':yomi,
                                         '未然形':gokan_kana + katsuyou['gobi'][0],
                                         '未然特殊':gokan_kana + mizen_sp,
                                         '未然ウ接続':gokan_kana + katsuyou['gobi'][4],
                                         '連用形':gokan_kana + katsuyou['gobi'][1],
                                         '連用タ接続':gokan_kana + renyou_ta,
                                         '仮定形':gokan_kana + katsuyou['gobi'][3],
                                         '命令ｅ':gokan_kana + katsuyou['gobi'][3],
                                         '仮定縮約1':gokan_kana + katsuyou['gobi'][5],
                                         '体言接続特殊':gokan_kana + taigen_sp,
                                         '体言接続特殊2':(gokan_kana + taigen_sp)[:-1] # 体言接続から語尾'ん'欠落したもの
                                         } 
                            # ID,コスト取得
                            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)
                            
                            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana) 
                                
                    else:    

                        # 音便変化
                        if katsuyou_line == 'タ':
                            renyou_ta = 'っ'
                        elif katsuyou_line in ['ナ','バ','マ']:
                            renyou_ta = 'ん'
                        elif katsuyou_line == 'ガ':
                            renyou_ta = 'い'     
                        elif katsuyou_line == 'カ':
                            if basicform[-2:] in ['いく','行く','逝く']: # カ行促音便
                                renyou_ta = 'っ'
                                katsuyou1 += '促音便'
                            elif basicform[-2:] == 'ゆく': # カ行促音便ユク
                                renyou_ta = ''
                                katsuyou1 += '促音便ユク'
                            else:
                                renyou_ta = 'い' # カ行イ音便
                                katsuyou1 += 'イ音便'
                                
                        elif katsuyou_line == 'ワ':
                            if basicform[-2:] in ['問う','乞う','沿う','ゆう','食う','すう','負う']: # ワ行ウ音便
                                renyou_ta = 'う'
                                katsuyou1 += 'ウ音便'
                            else:
                                renyou_ta = 'っ'
                                katsuyou1 += '促音便'
                        
                        if katsuyou_line != 'ワ': # ワ行には仮定縮約がない
                        
                            katsuyou2 = {'基本形':basicform,
                                         '未然形':gokan + katsuyou['gobi'][0],
                                         '未然ウ接続':gokan + katsuyou['gobi'][4],
                                         '連用形':gokan + katsuyou['gobi'][1],
                                         '連用タ接続':gokan + renyou_ta,
                                         '仮定形':gokan + katsuyou['gobi'][3],
                                         '命令ｅ':gokan + katsuyou['gobi'][3],
                                         '仮定縮約1':gokan + katsuyou['gobi'][5]
                                         }
                            yomi_kana = {'基本形':yomi,
                                         '未然形':gokan_kana + katsuyou['gobi'][0],
                                         '未然ウ接続':gokan_kana + katsuyou['gobi'][4],
                                         '連用形':gokan_kana + katsuyou['gobi'][1],
                                         '連用タ接続':gokan_kana + renyou_ta,
                                         '仮定形':gokan_kana + katsuyou['gobi'][3],
                                         '命令ｅ':gokan_kana + katsuyou['gobi'][3],
                                         '仮定縮約1':gokan_kana + katsuyou['gobi'][5]
                                         }      
                            # ID,コスト取得
                            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic)           

                            if katsuyou1 == '五段・カ行促音便ユク':
                                del katsuyou2['連用タ接続']
                                del yomi_kana['連用タ接続']
                            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)                           
                            
                                
                        else:
                            katsuyou2 = {'基本形':basicform,
                                         '未然形':gokan + katsuyou['gobi'][0],
                                         '未然ウ接続':gokan + katsuyou['gobi'][4],
                                         '連用形':gokan + katsuyou['gobi'][1],
                                         '連用タ接続':gokan + renyou_ta,
                                         '仮定形':gokan + katsuyou['gobi'][3],
                                         '命令ｅ':gokan + katsuyou['gobi'][3],
                                         }
                            yomi_kana = {'基本形':yomi,
                                         '未然形':gokan_kana + katsuyou['gobi'][0],
                                         '未然ウ接続':gokan_kana + katsuyou['gobi'][4],
                                         '連用形':gokan_kana + katsuyou['gobi'][1],
                                         '連用タ接続':gokan_kana + renyou_ta,
                                         '仮定形':gokan_kana + katsuyou['gobi'][3],
                                         '命令ｅ':gokan_kana + katsuyou['gobi'][3],
                                         }   
                            # ID,コスト取得
                            l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic) 
                            
                            entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)                             
                    
                    
            else:
                katsuyou1 = '一段'
                katsuyou2 = {'基本形':basicform,
                             '未然形':gokan,
                             '未然ウ接続':gokan + 'よ',
                             '連用形':gokan,
                             '仮定形':gokan + 'れ',
                             '命令ｙｏ':gokan + 'よ',
                             '命令ｒｏ':gokan + 'ろ',
                             '仮定縮約1':gokan + 'りゃ',
                             '体言接続特殊':gokan + 'ん'
                             }
                yomi_kana = {'基本形':yomi,
                             '未然形':gokan_kana,
                             '未然ウ接続':gokan_kana + 'よ',
                             '連用形':gokan_kana,
                             '仮定形':gokan_kana + 'れ',
                             '命令ｙｏ':gokan_kana + 'よ',
                             '命令ｒｏ':gokan_kana + 'ろ',
                             '仮定縮約1':gokan_kana + 'りゃ',
                             '体言接続特殊':gokan_kana + 'ん'
                             }    
                # ID,コスト取得
                l_ids,r_ids,costs = costcalc(yomi,katsuyou1,dic) 
                
                entries = gen_entries(basicform, w_class, katsuyou1, l_ids, r_ids, costs, katsuyou2, yomi_kana)  

    '''
    #spreadsheet出力
    
    hyousou = worksheet.col_values(1)
    last_row = len(hyousou) + 1  
    update_range = worksheet.range('a{0}:m{1}'.format(last_row, last_row + len(entries) -1))

    k = 0
    for i in range(len(entries)):    
        for i,v in enumerate(entries[i].values()):
            if i in [1,2,3]:
                update_range[k].value = int(v)
            else:
                update_range[k].value = v
            k += 1
    
    worksheet.update_cells(update_range)
    

    # wikidump csv出力
    
    print("wikidump読み込み中..",end="")
    #with open("/home/yusuke/wikidump.csv", "a", encoding="utf-8") as f: #追記
    with open("/home/yusuke/wikidump_anime.csv", "a", encoding="utf-8") as f: #追記
        writer = csv.DictWriter(f, [k for k, v in entries[0].items()])
        writer.writerows(entries)
    print("done.")
    '''
    return entries
    

if __name__=='__main__':
      
    
    # 過去の登録を読込 重複チェック用(adj,verbのみ)
    print("reading dics..",end="")
    with open("/opt/mecab-ipadic-neologd/build/mecab-ipadic-2.7.0-20070801-neologd-20200910/Adj.csv", "r", encoding="utf_8", newline="") as f:
        reader = csv.reader(f)
        adj_l = [r for r in reader]
    with open("/opt/mecab-ipadic-neologd/build/mecab-ipadic-2.7.0-20070801-neologd-20200910/Verb.csv", "r", encoding="utf_8", newline="") as f:
        reader = csv.reader(f)
        verb_l = [r for r in reader]        
    print("done.")
   

    while True:
        w_class = input("品詞:")
        if w_class == '動詞':         
            basicform = input("基本形:")
            yomi = input("読み仮名(平仮名):")
            denyform = input("否定形(～ず):")
            result = dictadd(w_class,basicform,denyform,yomi,verb_l)
            pprint.pprint(result)
        elif w_class == '形容詞':
            basicform = input("基本形:")
            denyform = ''
            yomi = input("読み仮名(平仮名):")
            result = dictadd(w_class,basicform,denyform,yomi,adj_l)
            pprint.pprint(result)
        else:
            print("品詞入力エラー")

        
    

