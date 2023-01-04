from django import template
import re
register = template.Library() # Djangoのテンプレートタグライブラリ

MENTION = re.compile(r'[@＠][a-zA-Z_0-9]+') # \wがうまくいかない?
    
TAG = re.compile(r'<[a-z].+>')
TAGHIDDEN = re.compile(r'__TAGHIDDEN__')
@register.filter()
def highlight_keys(text,keys):
    """ keys = 'ストーリー,物語,..' 
        ・textはhtmlタグが含まれるためタグ判定が必要(タグ内部は置換しない)
        →日本語のみ、あるいはタグに含まれない程度の文字数制限でクリアできそう
        単語から文末尾までハイライトしたい場合、
        ・複数ある場合どうするか？
        subの置換回数1設定で
    """

    alltags = TAG.findall(text)
    text = TAG.sub('__TAGHIDDEN__',text)
    
    #print('keys',keys)
    if keys:
        #print('keys',keys)
        keys_l = keys.split(',')
        
        keys_l = ['('+k+r'[^。\.!！\?？…・\s#<>]*)' for k in keys_l]
        match_keyword = ''
        for i in range(len(keys_l)):
            match_keyword += r'\{0}'.format(i+1)
        text = re.sub('|'.join(keys_l),r'<span style="font-weight:bold;">{0}</span>'.format(match_keyword),text,1)
    else:
        pass
    
    # 隠したtagを戻す
    for tag in alltags:
        text = TAGHIDDEN.sub(tag,text,1) # 1回のみ置換(必ず左から置換される)
    return text


@register.filter()
def highlight_only_keys(text,keys_l):
    """ リアルタイム検索用ハイライト
    単語のみハイライトさせる(英字の大文字小文字は区別。LISA検索でlisaは強調されない)
    keys = 検索している単語リスト(NOT単語は含まない) ex.['犬','猫']
    
    """


    if len(keys_l) == 0:
        return text
    ### tag内のキーワードはすべてハイライトしない(textにハッシュタグはhtmlタグとともに含まれる) ###
    # 全tagを保存
    alltags = TAG.findall(text) # 文字列listで返る['<a href ...>ABC</a>','<font..>D</font>',..]
    # keysで検索されないように#TAGHIDDEN#で全て置換する
    text = TAG.sub('__TAGHIDDEN__',text)

    # 括弧をつけて置換単語を保持する
    keys_l = ['(' + k + ')' for k in keys_l]
    match_keyword = ''
    for i in range(len(keys_l)):
        match_keyword += r'\{0}'.format(i+1)

    # 正規表現化
    matched_l = re.findall('|'.join(keys_l),text)
    #print('matched l',matched_l)
    # 一度に全単語を置換（一つ一つやると<b>タグが被る可能性ある ex. "犬と猫と犬"→"<b><b>犬</b></b>と<b>猫</b>と犬"
    text = re.sub('|'.join(keys_l),r'<span style="background-color: #fffacd">{0}</span>'.format(match_keyword),text)
    #print('text',text)
   
    # 隠したtagを戻す
    for tag in alltags:
        text = TAGHIDDEN.sub(tag,text,1) # 1回のみ置換(必ず左から置換される)
    return text


@register.filter()
def quiz_answer(value):
    """ 解答表示用に-と()を非表示"""
    value = re.sub(r"-"," ",value)
    return re.sub(r"\(.+\)$","",value)


@register.filter()
def get_ratio(value,value2):
    
    return str(int((value*100/value2 * 2 + 1) // 2))+"%"

@register.filter()
def to_str(value):
    return str(value)


@register.filter()
def to_int(value):
    return int(value)

# カスタムフィルタとして登録する
@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)


HTAG = re.compile(r',\[.+$')
TMP_SHARP = re.compile(r'hashtag/#')

# カスタムフィルタとして登録する
@register.filter(name='urlize_link')
def urlize_link(value,urls):
    """
        ハッシュタグ,メンションをリンクに変換.
    """

    ls = HTAG.search(urls).group().translate(str.maketrans({" ":"","'":"",",":"|"}))[2:-1].split("|")
    #print('A',ls)
    if ls != ['']:
        # 長いハッシュタグから置換する 
        ##(ex. #travis # travisjapan の場合,#travisjapanを先に検索する    
        ls = ['(#'+l+')' for l in sorted(ls,key=len,reverse=True)]
        #print('Ls',ls)
        match_keyword = ''
        for i in range(len(ls)):
            match_keyword += r'\{0}'.format(i+1) # r'\1\2..'
        #print('match_keyword',match_keyword)
        
        ls = "|".join(ls)
        #print('ls2',ls)
        
        value = re.sub(ls,r"<a href='https://twitter.com/hashtag/{0}?src=hashtag_click' target='_blank'>{0}</a>".format(match_keyword),value)
        value = TMP_SHARP.sub(r"hashtag/",value)
        #print('value',value)
    
# MENTION
    ls = MENTION.findall(value)

    for l in ls:      
        value = value.replace(l,r"<a href='https://twitter.com/{0}' target='_blank'>{1}</a>".format(l[1:],l))

# url(画像以外)をdisplay urlに変換
    
    urls = urls.split(',')

    if urls[0] == 'None':
        #print('OK')
        return value
    
    # adsense用 画像一旦除外
    #value = value.replace(urls[0],urls[0])
    value = value.replace(urls[0],r"<a href='{0}' rel='nofollow' target='_blank'>{1}</a>".format(urls[0],urls[1]))

    return value

    
EXP = re.compile(r'\.[^.]+$') # 拡張子(.jpg .tiff)
MEDIA = re.compile(r'/media/')
 
@register.filter(name='urlize_media')
def urlize_media(value,urls):
    """urls = "media_url_truncated, media_url, t_id """
    
    
    urls = urls.split(',')
    if urls[0] == 'None':
        return value
# media_url(https~)をmodernフォーマットに変換
# modern https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/entities#photo_format
    fileexp = EXP.search(urls[1]).group()[1:] # ドット除外   
    #print(fileexp)
    if MEDIA.search(urls[1]):
        urls[1] = EXP.sub(r'?format={0}&name=thumb'.format(fileexp),urls[1]) 
    else:
        urls[1] = urls[1] + ':thumb'

    value = value.replace(urls[0],
                          r"<br><a href='{0}' rel='nofollow' target='_blank'><img class='lazyload' data-src={1} width='150' height='150' alt='photo in tweet'></a>".format(urls[2],urls[1]))

    
    return value


@register.filter(name='urlize_media_ajax')
def urlize_media_ajax(value,urls):
    """ajax用 lazyloadなし """
    
    
    urls = urls.split(',')
    if urls[0] == 'None':
        return value
# media_url(https~)をmodernフォーマットに変換
# modern https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/entities#photo_format
    EXP = re.compile(r'\.[^.]+$') # 拡張子(.jpg .tiff)
    MEDIA = re.compile(r'/media/')
    fileexp = EXP.search(urls[1]).group()[1:] # ドット除外   
    #print(fileexp)
    if MEDIA.search(urls[1]):
        urls[1] = EXP.sub(r'?format={0}&name=thumb'.format(fileexp),urls[1]) 
    else:
        urls[1] = urls[1] + ':thumb'

    value = value.replace(urls[0],
                          r"<br><a href='{0}' rel='nofollow' target='_blank'><img src={1} width='150' height='150' alt='photo in tweet'></a>".format(urls[2],urls[1]))

    
    return value


@register.filter(name='join_dash')
def join_dash(var,args):
  
    return "%s-%s" % (var,args)


# カスタムフィルタの引数が3つ以上取れないため、urlとdisplay_urlを文字列として結合して渡す
@register.filter(name='join_comma')
def join_comma(var,args):
    return "%s,%s" % (var,args)

# media urlは除去(別途aタグ付与)
@register.filter(name='del_media')
def del_media(value,url):
    
    if url==None:
        return value

    value = value.replace(url,'')
    
    return value

# for nlp
@register.filter(name='display_strong')
def display_strong(value,letter):
    """
        letterを強調表示html変換.
    """
    try:
        ls = re.findall(letter,value)
    except:
        print('l:',letter)
        print('v:',value)
        ls = []
    
    for l in ls:    
        if len(l) != 0:
            value = value.replace(l,"<strong>"+l+"</strong>")

    
    return value

