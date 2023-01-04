# -*- coding: utf-8 -*-
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.mail import EmailMessage
import os
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from sentiment.models import Comment

class mecab_addForm(forms.Form):

    artist = forms.ChoiceField(
        label='アーティスト名', # htmlで表示されるラベル
        required=True,
        initial=[('dish','DISH')],
        choices=[
                 ('lisa','LiSA',),
                 ('hinatazaka46','日向坂46'),
                 ('aoieir','藍井エイル'),
                 ('aimer','Aimer'),
                 ('yonezu_kenshi','米津玄師'),
                 ('dish','DISH'),
                 ('mwam','MWAM'),
                 ('sixtones','SixTONES'),
                 ('news','NEWS'),
                 ('kanjanieight','関ジャニ8'),
                 ('kat_tun','KAT-TUN'),
                 ('heysayjump','Hey! Say! JUMP'),
                 ('kismyft2','Kis-My-Ft2')
                 ],
        widget=forms.Select(attrs={'id':'アーティスト名_mecab'})
    )
    '''
    SixTONES
    KAT-TUN
    NEWS
    関ジャニ∞
    Hey! Say! JUMP
    Kis-My-Ft2
    Sexy Zone
    ジャニーズWEST
    King & Prince
    Snow Man
    なにわ男子
    '''
    target = forms.CharField(
        label='target',
        required=True,
        initial='名詞,動詞,形容詞,助動詞',
        widget=forms.TextInput(attrs={'id':'target','cols': '10', 'rows': '10'})
    )
    '''
    jaccard = forms.FloatField(
        label='jaccard>=',
        required=True,
        initial=0.5,
        validators=[MinValueValidator(0.01), MaxValueValidator(1)],
        widget=forms.NumberInput(attrs={'id':'jaccard'})
    )
    '''
    simpson = forms.FloatField(
        label='simpson>=',
        required=True,
        initial=0.1,
        validators=[MinValueValidator(0.01), MaxValueValidator(1)],
        widget=forms.NumberInput(attrs={'id':'simpson'})
    )
    min_num = forms.IntegerField(
        label='共起頻度>=',
        required=True,
        initial=50,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
        widget=forms.NumberInput(attrs={'id':'min_num'})
    )

    
class Step1_2Form(forms.Form):

    artist = forms.ChoiceField(
        label='アーティスト名',
        required=True,
        initial=['米津玄師'],
        choices=[('LiSA','LiSA',),('日向坂46','日向坂46'),('藍井エイル','藍井エイル'),('Aimer','Aimer'),('米津玄師','米津玄師'),('DISH','DISH'),('MWAM','MWAM'),('NiziU_30min','NiziU_30min'),('NiziU','NiziU_1month')],
        widget=forms.Select(attrs={'id':'artist'})
    )
    labeling = forms.ChoiceField(
        label='ラベル',
        required=True,
        initial=['n2'],
        choices=[('n2','n2'),('n1','n1'),('p1','p1'),('p2','p2')],
        widget=forms.Select(attrs={'id':'labeling'})
    )
    s_date = forms.DateTimeField(
        label='開始日付',
        required=False,
        initial='',
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=['%Y-%m-%d']
    )
    e_date = forms.DateTimeField(
    label='終了日付',
    required=False,
    initial='',
    widget=forms.DateInput(attrs={"type": "date"}),
    input_formats=['%Y-%m-%d']
    )
    
    grouping = forms.ChoiceField(
        label='分類方法',
        required=True,
        initial=['頻出語S'],
        choices=[(1,'頻出語S'),(2,'頻出語S+V')],
        widget=forms.Select(attrs={'id':'grouping'})
    )
        
    
class FindForm(forms.Form):
    find = forms.CharField(label='アニメ検索', required=False, \
                           widget=forms.TextInput(attrs={'class':'form-control'}))

class SummaryForm(forms.Form):
    summary = forms.CharField(label='', required=False, \
                           widget=forms.Textarea(attrs={'id':'summary','cols': '100', 'rows': '10'}))
    n_sum = forms.ChoiceField(
        label='要約行数',
        required=False,
        initial=['3'],
        choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],
        widget=forms.Select(attrs={'id':'n_sum'})
    )
    s_kugiri = forms.ChoiceField(
        label='文章区切り',
        required=False,
        initial=['改行'],
        choices=[('\r\n','改行'),('。','句点')],
        widget=forms.Select(attrs={'id':'s_kugiri'})
    )

class ReasonForm(forms.Form):
    w_dist = forms.ChoiceField(
        label='距離',
        required=True,
        initial=['5'],
        choices=[('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7')\
                 ,('8','8'),('9','9'),('10','10')],
        widget=forms.Select(attrs={'id':'w_dist'})
    )
    n_output = forms.ChoiceField(
        label='出力枠',
        required=True,
        initial=['15'],
        choices=[('10','10'),('15','15'),('20','20'),('25','25'),('30','30'),('35','35')\
                 ,('40','40'),('45','45'),('50','50')],
        widget=forms.Select(attrs={'id':'w_dist'})
    )
    stopwords = forms.CharField(label='stopwords', required=False,            
            initial=("LISA,の,w,れる,こと,ちゃん,すぎ,ー,する,"
            "ある,さん,俺,やつ,てる,なる,さ,ない,やる,ω,ん,思う,"
            "そう,方,いる,みたい,ところ,僕,ちゃう,自分,奴,ぶり,"
            "的,しまう,あれ,もの,私,まじ,あと,これ,よう,られる,"
            "せる,事,とき,しよう,それ,マジで,せい,笑,(),皆さん,"
            "でる,感,気,だし,きた,くれる"),
            widget=forms.Textarea(attrs={'id':'stoopwords','cols': '100', 'rows': '3'}))
    
    def clean_stopwords(self):
        stopwords = self.cleaned_data['stopwords']
        if '、' in stopwords:
            raise forms.ValidationError('無効な文字検出')
        return stopwords
   
    
   # 日付フィルタ
class DateForm(forms.Form):
    
    date_filter = forms.ChoiceField(
        label='Period',
        required=False,
        initial=['1'],
        choices=[('1','1 day'),('2','1 week'),('3','1 month')],
        widget=forms.Select(attrs={'id':'date_filter'})
    )


class CharacterForm(forms.Form):
    
    character_filter = forms.ChoiceField(
        label='Character',
        required=False,
        initial=['セーラーマーズ'],
        choices=[('セーラームーン','セーラームーン'),('セーラーサターン','セーラーサターン'),('セーラージュピター','セーラージュピター'),('セーラーマーキュリー','セーラーマーキュリー'),('セーラービーナス','セーラービーナス'),('セーラーヴィーナス','セーラーヴィーナス'),('セーラーV','セーラーV'),('セーラーマーズ','セーラーマーズ'),('ちびムーン','ちびムーン'),('セーラーウラヌス','セーラーウラヌス'),('セーラーネプチューン','セーラーネプチューン'),('セーラープルート','セーラープルート'),('月野うさぎ','月野うさぎ'),('プリンセス・セレニティ','プリンセス・セレニティ'),('水野亜美','水野亜美'),('火野レイ','火野レイ'),('地場衛','地場衛'),('木野まこと','木野まこと'),('愛野美奈子','愛野美奈子'),('ちびうさ','ちびうさ'),('天王はるか','天王はるか'),('海王みちる','海王みちる'),('冥王せつな','冥王せつな'),('土萠ほたる','土萠ほたる'),('タキシード仮面','タキシード仮面'),('タキシードマスク','タキシードマスク'),('プリンス・エンディミオン','プリンス・エンディミオン'),('ネヘレニア','ネヘレニア'),('鬼滅','鬼滅'),('炭治郎','炭治郎'),('禰豆子','禰豆子'),('善逸','善逸'),('嘴平伊之助','嘴平伊之助'),('栗花落カナヲ','栗花落カナヲ'),('玄弥','玄弥'),('冨岡義勇','冨岡義勇'),('胡蝶しのぶ','胡蝶しのぶ'),('煉獄','煉獄'),('宇髄','宇髄'),('無一郎','無一郎'),('甘露寺','甘露寺'),('悲鳴嶼','悲鳴嶼'),('伊黒','伊黒'),('不死川','不死川'),('胡蝶カナエ','胡蝶カナエ'),('猗窩座','猗窩座'),('神崎アオイ','神崎アオイ'),('鬼舞辻','鬼舞辻'),('産屋敷','産屋敷'),('輝利哉','輝利哉'),('真菰','真菰'),('ワニ先生','ワニ先生'),('鱗滝','鱗滝'),('桑島慈悟郎','桑島慈悟郎'),('中原すみ','中原すみ'),('寺内きよ','寺内きよ'),('高田なほ','高田なほ'),('鉄珍','鉄珍'),('鋼鐵塚','鋼鐵塚'),('鉄穴森','鉄穴森'),('黒死牟','黒死牟'),('魘夢','魘夢'),('槇寿郎','槇寿郎'),('瑠火','瑠火'),('千寿郎','千寿郎'),('杏寿郎','杏寿郎'),('堕姫','堕姫'),('松衛門','松衛門'),('銀子','銀子'),('うこぎ','うこぎ'),('チュン太郎','チュン太郎'),('獪岳','獪岳'),('無惨','無惨'),('妓夫太郎','妓夫太郎'),('ぎゅうたろう','ぎゅうたろう'),('ソードアート','ソードアート'),('SAO','SAO'),('桐ヶ谷和人','桐ヶ谷和人'),('キリト','キリト'),('結城明日奈','結城明日奈'),('アスナ','アスナ'),('ユージオ','ユージオ'),('ツーベルク','ツーベルク'),('ティーゼ','ティーゼ'),('ウンベール','ウンベール'),('ロニエ','ロニエ'),('フィゼル','フィゼル'),('リネル','リネル'),('ファナティオ','ファナティオ'),('アズリカ','アズリカ'),('リーバンテイン','リーバンテイン'),('ソルティリーナ','ソルティリーナ'),('ゴルゴロッソ','ゴルゴロッソ'),('兎沢深澄','兎沢深澄'),('エギル','エギル'),('キバオウ','キバオウ'),('現実主義勇者','現実主義勇者'),('ソーマ・カズヤ','ソーマ・カズヤ'),('リーシア','リーシア'),('アイーシャ・ウドガルド','アイーシャ・ウドガルド'),('ジュナ・ドーマ','ジュナ・ドーマ'),('ロロア・アミドニア','ロロア・アミドニア'),('ハクヤ・クオンミン','ハクヤ・クオンミン'),('ポンチョ・パナコッタ','ポンチョ・パナコッタ'),('トモエ・イヌイ','トモエ・イヌイ'),('ハルバート・マグナ','ハルバート・マグナ'),('カエデ・フォキシア','カエデ・フォキシア'),('カストール・バルガス','カストール・バルガス'),('カルラ・バルガス','カルラ・バルガス'),('ゲオルグ・カーマイン','ゲオルグ・カーマイン'),('アルベルト・エルフリーデン','アルベルト・エルフリーデン'),('エリシャ・エルフリーデン','エリシャ・エルフリーデン'),('ガイウス・アミドニア','ガイウス・アミドニア'),('異世界食堂','異世界食堂'),('転生したらスライムだった件','転生したらスライムだった件'),('リムル','リムル'),('狼王','狼王'),('ヴェルドラ','ヴェルドラ'),('クロエ・オベル','クロエ・オベル'),('井沢静江','井沢静江'),('転スラ','転スラ'),('ベニマル','ベニマル'),('シュナ','シュナ'),('シオン','シオン'),('ソウエイ','ソウエイ'),('ハクロウ','ハクロウ'),('クロベエ','クロベエ'),('リグルド','リグルド'),('リグル','リグル'),('ゴブタ','ゴブタ'),('ランガ','ランガ'),('カイジン','カイジン'),('ゲルド','ゲルド'),('ガビル','ガビル'),('ソーカ','ソーカ'),('ベスター','ベスター'),('トレイニー','トレイニー'),('ヨウム','ヨウム'),('ディアブロ','ディアブロ'),('ミュウラン','ミュウラン'),('智慧之王','智慧之王'),('クロエ','クロエ'),('大賢者','大賢者'),('プラチナエンド','プラチナエンド'),('進化の実','進化の実'),('吸血鬼すぐ死ぬ','吸血鬼すぐ死ぬ'),('ドラルク','ドラルク'),('ヒナイチ','ヒナイチ'),('半田桃','半田桃'),('フクマ','フクマ'),('吸血鬼ロナルド','吸血鬼ロナルド'),('見える子ちゃん','見える子ちゃん'),('四谷みこ','四谷みこ'),('二暮堂ユリア','二暮堂ユリア'),('百合川ハナ','百合川ハナ'),('四谷恭介','四谷恭介'),('遠野善','遠野善'),('タケダミツエ','タケダミツエ'),('神童ロム','神童ロム'),('古見さん','古見さん'),('只野仁人','只野仁人'),('半妖の夜叉姫','半妖の夜叉姫'),('日暮とわ','日暮とわ'),('海賊王女','海賊王女'),('フェナ','フェナ'),('最果てのパラディン','最果てのパラディン'),('ありふれた職業で世界最強','ありふれた職業で世界最強'),('南雲ハジメ','南雲ハジメ'),('シア・ハウリア','シア・ハウリア'),('ティオ・クラルス','ティオ・クラルス'),('白崎香織','白崎香織'),('八重樫雫','八重樫雫'),('畑山愛子','畑山愛子'),('坂上龍太郎','坂上龍太郎'),('檜山大介','檜山大介'),('中村恵里','中村恵里'),('谷口鈴','谷口鈴'),('園部優花','園部優花'),('玉井淳史','玉井淳史'),('宮崎奈々','宮崎奈々'),('菅原妙子','菅原妙子'),('清水幸利','清水幸利'),('遠藤浩介','遠藤浩介'),('オスカー・オルクス','オスカー・オルクス'),('ミレディ・ライセン','ミレディ・ライセン'),('その着せ替え人形は恋をする','その着せ替え人形は恋をする'),('着せ恋','着せ恋'),('五条新菜','五条新菜'),('喜多川海夢','喜多川海夢'),('乾紗寿叶','乾紗寿叶'),('乾心寿','乾心寿'),('菅谷乃羽','菅谷乃羽')],
        widget=forms.Select(attrs={'id':'character_filter'})
    )

'''
class CharacterForm(forms.Form):
    character_filter = forms.CharField(
        label='Character',
        required=False,
        widget=forms.TextInput(attrs={'id':'character_filter','cols': '100', 'rows': '10'})
    )
'''    
class AnimeForm(forms.Form):
    
    anime_filter = forms.ChoiceField(
        label='Anime',
        required=False,
        initial=['セーラームーン'],
        choices=[('セーラームーン','セーラームーン'),('鬼滅の刃','鬼滅の刃'),('転スラ','転スラ'),('現実','現実'),('異世界食堂','異世界食堂'),('プラチナエンド','プラチナエンド'),('進化の実','進化の実'),('吸血鬼すぐ死ぬ','吸血鬼すぐ死ぬ'),('見える子ちゃん','見える子ちゃん'),('古見さん','古見さん'),('半妖の夜叉姫','半妖の夜叉姫'),('海賊王女','海賊王女'),('最果てのパラディン','最果てのパラディン'),('ありふれた職業で世界最強','ありふれた職業で世界最強'),('着せ恋','着せ恋')],
        widget=forms.Select(attrs={'id':'anime_filter'})
    )

    
        
class GetTweetForm(forms.Form):
 
    tweet_days = forms.IntegerField(
        label='Days',
        required=True,
        initial=7,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        widget=forms.NumberInput(attrs={'id':'tweet_days'})
    )
    
    anime_filter = forms.ChoiceField(
        label='Anime',
        required=False,
        choices=[('',''),('salormoon','salormoon'),('鬼滅','鬼滅'),('現実','現実'),('異世界食堂','異世界食堂'),('転スラ','転スラ'),('プラチナエンド','プラチナエンド'),('進化の実','進化の実'),('吸血鬼すぐ死ぬ','吸血鬼すぐ死ぬ'),('見える子ちゃん','見える子ちゃん'),('古見さん','古見さん'),('半妖の夜叉姫','半妖の夜叉姫'),('海賊王女','海賊王女'),('最果てのパラディン','最果てのパラディン'),('ありふれた職業で世界最強','ありふれた職業で世界最強'),('着せ恋','着せ恋')],
        widget=forms.Select(attrs={'id':'anime_filter'})
    )
    character_from = forms.IntegerField(
        label='--From',
        required=False,
        widget=forms.NumberInput(attrs={'id':'character_from'})
    )
        
    character_filter= forms.ChoiceField(
        label='Character',
        required=False,
        choices=[('',''),('セーラームーン','セーラームーン'),('セーラーサターン','セーラーサターン'),('セーラージュピター','セーラージュピター'),('セーラーマーキュリー','セーラーマーキュリー'),('セーラービーナス','セーラービーナス'),('セーラーヴィーナス','セーラーヴィーナス'),('セーラーV','セーラーV'),('セーラーマーズ','セーラーマーズ'),('ちびムーン','ちびムーン'),('セーラーウラヌス','セーラーウラヌス'),('セーラーネプチューン','セーラーネプチューン'),('セーラープルート','セーラープルート'),('月野うさぎ','月野うさぎ'),('プリンセス・セレニティ','プリンセス・セレニティ'),('水野亜美','水野亜美'),('火野レイ','火野レイ'),('地場衛','地場衛'),('木野まこと','木野まこと'),('愛野美奈子','愛野美奈子'),('ちびうさ','ちびうさ'),('天王はるか','天王はるか'),('海王みちる','海王みちる'),('冥王せつな','冥王せつな'),('土萠ほたる','土萠ほたる'),('タキシード仮面','タキシード仮面'),('タキシードマスク','タキシードマスク'),('プリンス・エンディミオン','プリンス・エンディミオン'),('ネヘレニア','ネヘレニア'),('鬼滅','鬼滅'),('炭治郎','炭治郎'),('禰豆子','禰豆子'),('善逸','善逸'),('嘴平伊之助','嘴平伊之助'),('栗花落カナヲ','栗花落カナヲ'),('玄弥','玄弥'),('冨岡義勇','冨岡義勇'),('胡蝶しのぶ','胡蝶しのぶ'),('煉獄','煉獄'),('宇髄','宇髄'),('無一郎','無一郎'),('甘露寺','甘露寺'),('悲鳴嶼','悲鳴嶼'),('伊黒','伊黒'),('不死川','不死川'),('胡蝶カナエ','胡蝶カナエ'),('猗窩座','猗窩座'),('神崎アオイ','神崎アオイ'),('鬼舞辻','鬼舞辻'),('産屋敷','産屋敷'),('輝利哉','輝利哉'),('真菰','真菰'),('ワニ先生','ワニ先生'),('鱗滝','鱗滝'),('桑島慈悟郎','桑島慈悟郎'),('中原すみ','中原すみ'),('寺内きよ','寺内きよ'),('高田なほ','高田なほ'),('鉄珍','鉄珍'),('鋼鐵塚','鋼鐵塚'),('鉄穴森','鉄穴森'),('黒死牟','黒死牟'),('魘夢','魘夢'),('槇寿郎','槇寿郎'),('瑠火','瑠火'),('千寿郎','千寿郎'),('杏寿郎','杏寿郎'),('堕姫','堕姫'),('松衛門','松衛門'),('銀子','銀子'),('うこぎ','うこぎ'),('チュン太郎','チュン太郎'),('獪岳','獪岳'),('ソードアート','ソードアート'),('SAO','SAO'),('桐ヶ谷和人','桐ヶ谷和人'),('キリト','キリト'),('結城明日奈','結城明日奈'),('アスナ','アスナ'),('ユージオ','ユージオ'),('ツーベルク','ツーベルク'),('ティーゼ','ティーゼ'),('ウンベール','ウンベール'),('ロニエ','ロニエ'),('フィゼル','フィゼル'),('リネル','リネル'),('ファナティオ','ファナティオ'),('アズリカ','アズリカ'),('リーバンテイン','リーバンテイン'),('ソルティリーナ','ソルティリーナ'),('ゴルゴロッソ','ゴルゴロッソ'),('兎沢深澄','兎沢深澄'),('エギル','エギル'),('キバオウ','キバオウ'),('転生したらスライムだった件','転生したらスライムだった件'),('リムル','リムル'),('狼王','狼王'),('ヴェルドラ','ヴェルドラ'),('クロエ・オベル','クロエ・オベル'),('井沢静江','井沢静江'),('現実主義勇者','現実主義勇者'),('ソーマ・カズヤ','ソーマ・カズヤ'),('リーシア','リーシア'),('アイーシャ・ウドガルド','アイーシャ・ウドガルド'),('ジュナ・ドーマ','ジュナ・ドーマ'),('ロロア・アミドニア','ロロア・アミドニア'),('ハクヤ・クオンミン','ハクヤ・クオンミン'),('ポンチョ・パナコッタ','ポンチョ・パナコッタ'),('トモエ・イヌイ','トモエ・イヌイ'),('ハルバート・マグナ','ハルバート・マグナ'),('カエデ・フォキシア','カエデ・フォキシア'),('カストール・バルガス','カストール・バルガス'),('カルラ・バルガス','カルラ・バルガス'),('ゲオルグ・カーマイン','ゲオルグ・カーマイン'),('アルベルト・エルフリーデン','アルベルト・エルフリーデン'),('エリシャ・エルフリーデン','エリシャ・エルフリーデン'),('ガイウス・アミドニア','ガイウス・アミドニア'),('異世界食堂','異世界食堂'),('プラチナエンド','プラチナエンド'),('進化の実','進化の実'),('吸血鬼すぐ死ぬ','吸血鬼すぐ死ぬ'),('ドラルク','ドラルク'),('ヒナイチ','ヒナイチ'),('半田桃','半田桃'),('フクマ','フクマ'),('見える子ちゃん','見える子ちゃん'),('四谷みこ','四谷みこ'),('二暮堂ユリア','二暮堂ユリア'),('百合川ハナ','百合川ハナ'),('四谷恭介','四谷恭介'),('遠野善','遠野善'),('タケダミツエ','タケダミツエ'),('神童ロム','神童ロム'),('古見さん','古見さん'),('只野仁人','只野仁人'),('半妖の夜叉姫','半妖の夜叉姫'),('日暮とわ','日暮とわ'),('海賊王女','海賊王女'),('フェナ','フェナ'),('最果てのパラディン','最果てのパラディン')],
        widget=forms.Select(attrs={'id':'character_filter'})
    )
    id_filter = forms.CharField(
        label='ID',
        required=False,
        widget=forms.TextInput(attrs={'id':'character_filter','cols': '100', 'rows': '10'})
    )

    
class GenSheetForm(forms.Form):
 
    date_from = forms.CharField(
        label='Date_from',
        required=True,
        initial='20210901',
        #validators=[MinValueValidator(0), MaxValueValidator(7)],
        widget=forms.TextInput(attrs={'id':'date_from'})
    )
    date_until = forms.CharField(
        label='Date_until',
        required=True,
        initial='20210907',
        #validators=[MinValueValidator(0), MaxValueValidator(7)],
        widget=forms.TextInput(attrs={'id':'date_until'})
    )
    max_length = forms.IntegerField(
        label='Max_length',
        required=True,
        initial=60,
        validators=[MinValueValidator(1), MaxValueValidator(280)],
        widget=forms.NumberInput(attrs={'id':'max_length'})
    )
    anime_sheet = forms.ChoiceField(
        label='Anime_sheet',
        required=True,
        initial=('',''),
        choices=[('',''),('セーラームーン','セーラームーン'),('鬼滅の刃','鬼滅の刃'),('転スラ','転スラ'),('現実','現実'),('異世界食堂','異世界食堂'),('プラチナエンド','プラチナエンド'),('進化の実','進化の実'),('吸血鬼すぐ死ぬ','吸血鬼すぐ死ぬ'),('見える子ちゃん','見える子ちゃん'),('古見さん','古見さん'),('半妖の夜叉姫','半妖の夜叉姫'),('海賊王女','海賊王女'),('最果てのパラディン','最果てのパラディン'),('ありふれた職業で世界最強','ありふれた職業で世界最強'),('着せ恋','着せ恋')],
       #validators=[MinValueValidator(0), MaxValueValidator(7)],
        widget=forms.Select(attrs={'id':'anime_sheet'})
    )
    gen_label = forms.ChoiceField(
        label='Gen_label',
        required=False,
        choices=[('n2','n2'),('n1','n1'),('e','e'),('p1','p1'),('p2','p2')],
        widget=forms.CheckboxSelectMultiple(attrs={'id':'gen_label'})
    )
    
class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=30,required=True)
    email = forms.EmailField(label='メールアドレス',required=True)
    title = forms.CharField(label='タイトル', max_length=30,required=True)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea,required=True)
    '''
    notbot = forms.BooleanField(
        label='botではありません',
        required=True,
        widget=forms.CheckboxInput()
    )
    '''
    captcha = ReCaptchaField(widget=ReCaptchaWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'form-control col-9'
        self.fields['name'].widget.attrs['placeholder'] = 'お名前をここに入力してください。'

        self.fields['email'].widget.attrs['class'] = 'form-control col-11'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスをここに入力してください。'

        self.fields['title'].widget.attrs['class'] = 'form-control col-11'
        self.fields['title'].widget.attrs['placeholder'] = 'タイトルをここに入力してください。'

        self.fields['message'].widget.attrs['class'] = 'form-control col-12'
        self.fields['message'].widget.attrs['placeholder'] = 'メッセージをここに入力してください。'

    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        subject = 'お問い合わせ {}'.format(title)
        message = '送信者名: {0}\nメールアドレス: {1}\nメッセージ:\n{2}'.format(name, email, message)
        from_email = 'support@purakome.net'
        to_list = [
            os.environ.get('EMAIL_HOST_USER')
        ]
        cc_list = [
            os.environ.get('EMAIL_CC')
            #email
        ]

        message = EmailMessage(subject=subject, body=message, from_email=from_email, to=to_list, cc=cc_list)
        message.send()    

class pn_detailForm(forms.Form):



    very_positive = forms.BooleanField(
        label='とても満足',
        required=False,
        widget=forms.CheckboxInput(attrs={'id':'very_positive'}),
    )   
    positive = forms.BooleanField(
        label='満足',
        required=False,
        widget=forms.CheckboxInput(attrs={'id':'positive'}),
    )   
    negative = forms.BooleanField(
        label='不満',
        required=False,
        widget=forms.CheckboxInput(attrs={'id':'negative'}),
    )    
    very_negative = forms.BooleanField(
        label='とても不満',
        required=False,
        widget=forms.CheckboxInput(attrs={'id':'very_negative'}),
    )   


       
class summarizeForm(forms.Form):

    summarize = forms.BooleanField(
        label='要約する',
        required=False,
        widget=forms.CheckboxInput(attrs={'id':'summarize_filter','onclick':'disable_keyword(this.checked);'}),
    )     

class keywordForm(forms.Form):

    keyword = forms.CharField(label='キーワード', max_length=30)
    keyword = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={'placeholder':'キーワード','id':'keyword_filter','onchange':'disable_summarize(value);','cols': '30', 'rows': '10'})
    )  

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('user_name','message')
   
    #captcha = ReCaptchaField(widget=ReCaptchaWidget())

 
    # overriding default form setting and adding bootstrap class
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs = {'placeholder': 'Enter name','class':'form-control'}
        self.fields['message'].widget.attrs = {'placeholder': '', 'class':'form-control', 'rows':'5'}

