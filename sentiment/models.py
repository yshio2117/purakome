from django.db import models
import datetime
from django.utils import timezone
from django.urls import reverse

# Create your models here.
           
class Prefectures(models.Model): # test

    prefecture = models.CharField(unique=True,null=True,max_length=10)
    map_id = models.CharField(unique=True,null=True,max_length=2)    

    def __str__(self):
        return self.prefecture
    
    class Meta:
        verbose_name = "Prefectures"
        verbose_name_plural = "Prefectures"  
    
        
class Official_names(models.Model): # パーティーション用

    index = models.PositiveSmallIntegerField(primary_key=True,default=0)
    #title = models.BooleanField(null=True, blank=True,default=False)
    official_name = models.CharField(unique=True,null=True,max_length=40)
    title_name = models.CharField(null=True,max_length=40)
    hidden = models.BooleanField(default=False) # ページに表示するか
    kind = models.PositiveSmallIntegerField(blank=True,default=1) # 0:anime, 1:character, 2:op, 3:ed
    url_name = models.CharField(unique=True,null=True,max_length=40) # uniqueにできる?
    past = models.BooleanField(default=False) # OA終了&過去ページ作成済みか
    short_name = models.CharField(null=True,max_length=40)  # <title>
    series = models.BooleanField(default=False) # 複数話続くか(trueの場合anime_weeksが自動作成される)
    quiz_key = models.CharField(null=True,default=None,max_length=80)

    def __str__(self):
        return str(self.index)+','+self.official_name+','+self.title_name+','+str(self.hidden)+','+str(self.kind)

    class Meta:
        verbose_name = "Official_names"
        verbose_name_plural = "Official_names"  
    
    
class Keywords(models.Model): # パーティーション用


    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT, default=0)
    keyword = models.CharField(unique=True,null=True,max_length=40)
    domestic = models.BooleanField(default=False) # アニメ内でのみ通用するキーワードか

    def __str__(self):
        return str(self.official_name)+','+str(self.keyword)

    class Meta:
        verbose_name = "Keywords"
        verbose_name_plural = "Keywords"  
        
        
class Tweetdata2(models.Model):

    up_date = models.DateTimeField(null=True,default=timezone.now) # データ取得日    
    t_id = models.URLField(primary_key=True)
    u_id = models.URLField(blank=True,null=True)
    t_date = models.DateTimeField()
    content = models.CharField(max_length=280)
    s_name = models.CharField(null=True,max_length=15)
    r_count = models.PositiveIntegerField(null=True,default=0)
    f_count = models.PositiveIntegerField(null=True,default=0)
# 以下20210906追加
    media_url =models.URLField(null=True)
    retweeted =models.BooleanField(default=False)
    hashtag = models.CharField(null=True,max_length=280)
    location = models.CharField(null=True,max_length=280)
# 以下20220110追加
    spam = models.BooleanField(default=False)
    wakachi = models.CharField(null=True,max_length=280) # wordcloud用 形容詞or形容動詞 '長い かわいい 美しい'
    
    
# 以下20220129追加
    u_name = models.CharField(null=True,max_length=50)
    p_image = models.URLField(null=True)
    verified = models.BooleanField(default=False)
    s_class = models.PositiveSmallIntegerField(null=True,default=2)
    t_id_char = models.CharField(null=True,max_length=30)
    entities_display_url = models.URLField(null=True)
    entities_url = models.URLField(null=True)
    
    media_url_truncated = models.URLField(null=True)
# summary用
    character1 = models.PositiveSmallIntegerField(default=0,null=True)
    character2 = models.PositiveSmallIntegerField(default=0,null=True)
    character3 = models.PositiveSmallIntegerField(default=0,null=True)
    character4 = models.PositiveSmallIntegerField(default=0,null=True)
    character5 = models.PositiveSmallIntegerField(default=0,null=True)

    title1 = models.PositiveSmallIntegerField(default=0,null=True)
    title2 = models.PositiveSmallIntegerField(default=0,null=True)
    title3 = models.PositiveSmallIntegerField(default=0,null=True)

    #prefecture = models.PositiveSmallIntegerField(default=0,null=True)
    prefecture = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=0)

    sum_title_text = models.PositiveSmallIntegerField(default=0,null=True)# 要約番号1~20
    sum_title = models.ForeignKey(Official_names, on_delete=models.DO_NOTHING, default=0,related_name='sum_title')
    sum_chara_text = models.PositiveSmallIntegerField(default=0,null=True)# 要約番号1~20
    sum_chara = models.ForeignKey(Official_names, on_delete=models.DO_NOTHING, default=0,related_name='sum_chara')
    sum_op_text = models.PositiveSmallIntegerField(default=0,null=True)# 要約番号1~20
    sum_op = models.ForeignKey(Official_names, on_delete=models.DO_NOTHING, default=0,related_name='sum_op')
    sum_ed_text = models.PositiveSmallIntegerField(default=0,null=True)# 要約番号1~20
    sum_ed = models.ForeignKey(Official_names, on_delete=models.DO_NOTHING, default=0,related_name='sum_ed')
    sum_cv_text = models.PositiveSmallIntegerField(default=0,null=True)# 要約番号1~20
    sum_cv = models.ForeignKey(Official_names, on_delete=models.DO_NOTHING, default=0,related_name='sum_cv')

    trend_no = models.PositiveSmallIntegerField(default=0,null=True)# trend1~10

    lang = models.PositiveSmallIntegerField(default=0)# 0:ja, 1:en
    translate = models.CharField(null=True,max_length=500) # lang:enの場合のみ


    def __str__(self):
        return '<'+str(self.s_class)+','+self.content + ','+ \
            datetime.datetime.strftime(self.t_date,'%Y-%m-%d %H:%M:%S')+','+str(self.t_id)+','+str(self.u_id)+'>'

    class Meta:
        verbose_name = "Tweetdata2"
        verbose_name_plural = "Tweetdata2"  


class Tweetdata3(models.Model):


    up_date = models.DateTimeField(null=True,default=timezone.now) # データ取得日
    
    t_id = models.URLField(primary_key=True)
    u_id = models.URLField(blank=True,null=True)
    t_date = models.DateTimeField()
    content = models.CharField(max_length=280)
    s_name = models.CharField(null=True,max_length=15)
    r_count = models.PositiveIntegerField(null=True,default=0)
    f_count = models.PositiveIntegerField(null=True,default=0)
# 以下20210906追加
    media_url =models.URLField(null=True)
    retweeted =models.BooleanField(default=False)
    hashtag = models.CharField(null=True,max_length=280)
    location = models.CharField(null=True,max_length=280)
# 以下20220110追加
    spam = models.BooleanField(default=False)
    wakachi = models.CharField(null=True,max_length=280) # wordcloud用 形容詞or形容動詞 '長い かわいい 美しい'


# 以下20220129追加
    u_name = models.CharField(null=True,max_length=50)
    p_image = models.URLField(null=True)
    verified = models.BooleanField(default=False)
    s_class = models.PositiveSmallIntegerField(null=True,default=2)
    t_id_char = models.CharField(null=True,max_length=30)  ###########unique不可
    entities_display_url = models.URLField(null=True)
    entities_url = models.URLField(null=True)

    media_url_truncated = models.URLField(null=True)

    lang = models.PositiveSmallIntegerField(default=0)# 0:ja, 1:en
    translate = models.CharField(null=True,max_length=500) # lang:enの場合のみ

    query = models.CharField(null=True,max_length=500) # 検索に使ったクエリ

    def __str__(self):
        return '<'+str(self.s_class)+','+self.content + ','+ \
            datetime.datetime.strftime(self.t_date,'%Y-%m-%d %H:%M:%S')+','+str(self.t_id)+','+str(self.u_id)+'>'

    class Meta:
        verbose_name = "Tweetdata3"
        verbose_name_plural = "Tweetdata3"


class Statistics1week(models.Model): # パーティーション用

    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)
    episode = models.PositiveSmallIntegerField(default=0,null=True)

    up_date = models.DateTimeField(null=True) # 更新日

    s_date = models.DateTimeField(null=True)# 作成した日時
    e_date = models.DateTimeField(null=True)
    p2_count_d1 = models.PositiveIntegerField(default=0)
    p1_count_d1 = models.PositiveIntegerField(default=0)
    n2_count_d1 = models.PositiveIntegerField(default=0)
    n1_count_d1 = models.PositiveIntegerField(default=0)
    p2_count_d2 = models.PositiveIntegerField(default=0)
    p1_count_d2 = models.PositiveIntegerField(default=0)
    n2_count_d2 = models.PositiveIntegerField(default=0)
    n1_count_d2 = models.PositiveIntegerField(default=0)
    p2_count_d3 = models.PositiveIntegerField(default=0)
    p1_count_d3 = models.PositiveIntegerField(default=0)
    n2_count_d3 = models.PositiveIntegerField(default=0)
    n1_count_d3 = models.PositiveIntegerField(default=0)
    p2_count_d4 = models.PositiveIntegerField(default=0)
    p1_count_d4 = models.PositiveIntegerField(default=0)
    n2_count_d4 = models.PositiveIntegerField(default=0)
    n1_count_d4 = models.PositiveIntegerField(default=0)
    p2_count_d5 = models.PositiveIntegerField(default=0)
    p1_count_d5 = models.PositiveIntegerField(default=0)
    n2_count_d5 = models.PositiveIntegerField(default=0)
    n1_count_d5 = models.PositiveIntegerField(default=0)
    p2_count_d6 = models.PositiveIntegerField(default=0)
    p1_count_d6 = models.PositiveIntegerField(default=0)
    n2_count_d6 = models.PositiveIntegerField(default=0)
    n1_count_d6 = models.PositiveIntegerField(default=0)
    p2_count_d7 = models.PositiveIntegerField(default=0)
    p1_count_d7 = models.PositiveIntegerField(default=0)
    n2_count_d7 = models.PositiveIntegerField(default=0)
    n1_count_d7 = models.PositiveIntegerField(default=0)

    p_tweet1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet1')
    p_tweet2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet2')
    p_tweet3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet3')
    p_tweet4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet4')
    p_tweet5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet5')
    p_tweet6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet6')
    p_tweet7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet7')
    p_tweet8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet8')
    p_tweet9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet9')
    p_tweet10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='p_tweet10')

    n_tweet1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet1')
    n_tweet2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet2')
    n_tweet3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet3')
    n_tweet4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet4')
    n_tweet5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet5')
    n_tweet6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet6')
    n_tweet7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet7')
    n_tweet8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet8')
    n_tweet9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet9')
    n_tweet10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, default='',related_name='n_tweet10')

# ENG
    ep_tweet1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet1')
    ep_tweet2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet2')
    ep_tweet3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet3')
    ep_tweet4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet4')
    ep_tweet5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet5')
    ep_tweet6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet6')
    ep_tweet7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet7')
    ep_tweet8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet8')
    ep_tweet9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet9')
    ep_tweet10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='ep_tweet10')

    en_tweet1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet1')
    en_tweet2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet2')
    en_tweet3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet3')
    en_tweet4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet4')
    en_tweet5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet5')
    en_tweet6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet6')
    en_tweet7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet7')
    en_tweet8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet8')
    en_tweet9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet9')
    en_tweet10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='en_tweet10')

    # wordcloud = models.ImageField()
    # trend
    # location
    # hashtag
    
    def get_absolute_url_title(self):
        return reverse('anime_episode', kwargs={'name' : self.official_name.url_name,
                                                'episode' : self.post.split('-')[1]
                                                })

    def __str__(self):
        return '<'+str(self.title)+','+str(self.character) +'>'

    class Meta:
        verbose_name = "Statistics1week"
        verbose_name_plural = "Statistics1week" 
       
 
class Summarys(models.Model):
    
    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)    
    episode = models.PositiveSmallIntegerField(default=0,null=True)
#要約文    
    summary_text1 = models.CharField(null=True,max_length=50) # 要約文
    summary_text2 = models.CharField(null=True,max_length=50) # 要約文
    summary_text3 = models.CharField(null=True,max_length=50) # 要約文
    summary_text4 = models.CharField(null=True,max_length=50) # 要約文
    summary_text5 = models.CharField(null=True,max_length=50) # 要約文
    summary_text6 = models.CharField(null=True,max_length=50) # 要約文
    summary_text7 = models.CharField(null=True,max_length=50) # 要約文
    summary_text8 = models.CharField(null=True,max_length=50) # 要約文
    summary_text9 = models.CharField(null=True,max_length=50) # 要約文
    summary_text10 = models.CharField(null=True,max_length=50) # 要約文
    summary_text11 = models.CharField(null=True,max_length=50) # 要約文
    summary_text12 = models.CharField(null=True,max_length=50) # 要約文
    summary_text13 = models.CharField(null=True,max_length=50) # 要約文
    summary_text14 = models.CharField(null=True,max_length=50) # 要約文
    summary_text15 = models.CharField(null=True,max_length=50) # 要約文
    summary_text16 = models.CharField(null=True,max_length=50) # 要約文
    summary_text17 = models.CharField(null=True,max_length=50) # 要約文
    summary_text18 = models.CharField(null=True,max_length=50) # 要約文
    summary_text19 = models.CharField(null=True,max_length=50) # 要約文
    summary_text20 = models.CharField(null=True,max_length=50) # 要約文
# 形態素
    summary_base1 = models.CharField(null=True,max_length=150) # 要約文
    summary_base2 = models.CharField(null=True,max_length=150) # 要約文
    summary_base3 = models.CharField(null=True,max_length=150) # 要約文
    summary_base4 = models.CharField(null=True,max_length=150) # 要約文
    summary_base5 = models.CharField(null=True,max_length=150) # 要約文
    summary_base6 = models.CharField(null=True,max_length=150) # 要約文
    summary_base7 = models.CharField(null=True,max_length=150) # 要約文
    summary_base8 = models.CharField(null=True,max_length=150) # 要約文
    summary_base9 = models.CharField(null=True,max_length=150) # 要約文
    summary_base10 = models.CharField(null=True,max_length=150) # 要約文
    summary_base11 = models.CharField(null=True,max_length=150) # 要約文
    summary_base12 = models.CharField(null=True,max_length=150) # 要約文
    summary_base13 = models.CharField(null=True,max_length=150) # 要約文
    summary_base14 = models.CharField(null=True,max_length=150) # 要約文
    summary_base15 = models.CharField(null=True,max_length=150) # 要約文
    summary_base16 = models.CharField(null=True,max_length=150) # 要約文
    summary_base17 = models.CharField(null=True,max_length=150) # 要約文
    summary_base18 = models.CharField(null=True,max_length=150) # 要約文
    summary_base19 = models.CharField(null=True,max_length=150) # 要約文
    summary_base20 = models.CharField(null=True,max_length=150) # 要約文
    
# 以下ネガティブ
    summary_text21 = models.CharField(null=True,max_length=50) # 要約文
    summary_text22 = models.CharField(null=True,max_length=50) # 要約文
    summary_text23 = models.CharField(null=True,max_length=50) # 要約文
    summary_text24 = models.CharField(null=True,max_length=50) # 要約文
    summary_text25 = models.CharField(null=True,max_length=50) # 要約文
    summary_text26 = models.CharField(null=True,max_length=50) # 要約文
    summary_text27 = models.CharField(null=True,max_length=50) # 要約文
    summary_text28 = models.CharField(null=True,max_length=50) # 要約文
    summary_text29 = models.CharField(null=True,max_length=50) # 要約文
    summary_text30 = models.CharField(null=True,max_length=50) # 要約文
    summary_text31 = models.CharField(null=True,max_length=50) # 要約文
    summary_text32 = models.CharField(null=True,max_length=50) # 要約文
    summary_text33 = models.CharField(null=True,max_length=50) # 要約文
    summary_text34 = models.CharField(null=True,max_length=50) # 要約文
    summary_text35 = models.CharField(null=True,max_length=50) # 要約文
    summary_text36 = models.CharField(null=True,max_length=50) # 要約文
    summary_text37 = models.CharField(null=True,max_length=50) # 要約文
    summary_text38 = models.CharField(null=True,max_length=50) # 要約文
    summary_text39 = models.CharField(null=True,max_length=50) # 要約文
    summary_text40 = models.CharField(null=True,max_length=50) # 要約文
# 形態素
    summary_base21 = models.CharField(null=True,max_length=150) # 要約文
    summary_base22 = models.CharField(null=True,max_length=150) # 要約文
    summary_base23 = models.CharField(null=True,max_length=150) # 要約文
    summary_base24 = models.CharField(null=True,max_length=150) # 要約文
    summary_base25 = models.CharField(null=True,max_length=150) # 要約文
    summary_base26 = models.CharField(null=True,max_length=150) # 要約文
    summary_base27 = models.CharField(null=True,max_length=150) # 要約文
    summary_base28 = models.CharField(null=True,max_length=150) # 要約文
    summary_base29 = models.CharField(null=True,max_length=150) # 要約文
    summary_base30 = models.CharField(null=True,max_length=150) # 要約文
    summary_base31 = models.CharField(null=True,max_length=150) # 要約文
    summary_base32 = models.CharField(null=True,max_length=150) # 要約文
    summary_base33 = models.CharField(null=True,max_length=150) # 要約文
    summary_base34 = models.CharField(null=True,max_length=150) # 要約文
    summary_base35 = models.CharField(null=True,max_length=150) # 要約文
    summary_base36 = models.CharField(null=True,max_length=150) # 要約文
    summary_base37 = models.CharField(null=True,max_length=150) # 要約文
    summary_base38 = models.CharField(null=True,max_length=150) # 要約文
    summary_base39 = models.CharField(null=True,max_length=150) # 要約文
    summary_base40 = models.CharField(null=True,max_length=150) # 要約文

# 新規要約か?
    new_summary1 = models.BooleanField(default=False)
    new_summary2 = models.BooleanField(default=False)
    new_summary3 = models.BooleanField(default=False)
    new_summary4 = models.BooleanField(default=False)
    new_summary5 = models.BooleanField(default=False)
    new_summary6 = models.BooleanField(default=False)
    new_summary7 = models.BooleanField(default=False)
    new_summary8 = models.BooleanField(default=False)
    new_summary9 = models.BooleanField(default=False)
    new_summary10 = models.BooleanField(default=False)
    new_summary11 = models.BooleanField(default=False)
    new_summary12 = models.BooleanField(default=False)
    new_summary13 = models.BooleanField(default=False)
    new_summary14 = models.BooleanField(default=False)
    new_summary15 = models.BooleanField(default=False)
    new_summary16 = models.BooleanField(default=False)
    new_summary17 = models.BooleanField(default=False)
    new_summary18 = models.BooleanField(default=False)
    new_summary19 = models.BooleanField(default=False)
    new_summary20 = models.BooleanField(default=False)
    new_summary21 = models.BooleanField(default=False)
    new_summary22 = models.BooleanField(default=False)
    new_summary23 = models.BooleanField(default=False)
    new_summary24 = models.BooleanField(default=False)
    new_summary25 = models.BooleanField(default=False)
    new_summary26 = models.BooleanField(default=False)
    new_summary27 = models.BooleanField(default=False)
    new_summary28 = models.BooleanField(default=False)
    new_summary29 = models.BooleanField(default=False)
    new_summary30 = models.BooleanField(default=False)
    new_summary31 = models.BooleanField(default=False)
    new_summary32 = models.BooleanField(default=False)
    new_summary33 = models.BooleanField(default=False)
    new_summary34 = models.BooleanField(default=False)
    new_summary35 = models.BooleanField(default=False)
    new_summary36 = models.BooleanField(default=False)
    new_summary37 = models.BooleanField(default=False)
    new_summary38 = models.BooleanField(default=False)
    new_summary39 = models.BooleanField(default=False)
    new_summary40 = models.BooleanField(default=False)
    
    related1 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related1') 
    related2 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related2') 
    related3 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related3') 
    related4 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related4') 
    related5 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related5') 
    related6 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related6') 
    related7 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related7') 
    related8 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related8') 
    related9 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related9') 
    related10 = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0,related_name='related10')   
 
    def __str__(self):
        return str(self.official_name) + ',' + str(self.summary_text1)

    class Meta:
        verbose_name = "Summarys"
        verbose_name_plural = "Summarys"  

        
class Trend_ranks(models.Model): # パーティーション用

    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)    
    episode = models.PositiveSmallIntegerField(default=0,null=True)

    trend1 = models.CharField(null=True,max_length=30) # trend tweet逆引きもしたい
    trend1_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend2 = models.CharField(null=True,max_length=30)
    trend2_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend3 = models.CharField(null=True,max_length=30)
    trend3_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend4 = models.CharField(null=True,max_length=30)
    trend4_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend5 = models.CharField(null=True,max_length=30)
    trend5_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend6 = models.CharField(null=True,max_length=30)
    trend6_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend7 = models.CharField(null=True,max_length=30)
    trend7_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend8 = models.CharField(null=True,max_length=30)
    trend8_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend9 = models.CharField(null=True,max_length=30)
    trend9_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    trend10 = models.CharField(null=True,max_length=30)
    trend10_count = models.PositiveSmallIntegerField(default=0,null=True)
    
    def __str__(self):
        return str(self.official_name) + ',' + str(self.trend1)

    class Meta:
        verbose_name = "Trend_ranks"
        verbose_name_plural = "Trend_ranks"  


class Pref_ranks(models.Model): # パーティーション用

    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)    
    episode = models.PositiveSmallIntegerField(default=0,null=True)

    pref1_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref2_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref3_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref4_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref5_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref6_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref7_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref8_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref9_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref10_count = models.PositiveSmallIntegerField(default=0,null=True)
# 以下n
    pref11_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref12_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref13_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref14_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref15_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref16_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref17_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref18_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref19_count = models.PositiveSmallIntegerField(default=0,null=True)
    pref20_count = models.PositiveSmallIntegerField(default=0,null=True)


    pref1_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref1_name',to_field="prefecture") # to_filedのデフォルトはprimary key. 指定する場合はuniqueカラムを指定必要.

    pref2_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref2_name',to_field="prefecture")

    pref3_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref3_name',to_field="prefecture")

    pref4_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref4_name',to_field="prefecture")

    pref5_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref5_name',to_field="prefecture")

    pref6_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref6_name',to_field="prefecture")

    pref7_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref7_name',to_field="prefecture")

    pref8_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref8_name',to_field="prefecture")

    pref9_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref9_name',to_field="prefecture")

    pref10_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref10_name',to_field="prefecture")    

##### 以下n

    pref11_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref11_name',to_field="prefecture") # to_filedのデフォルトはprimary key. 指定する場合はuniqueカラムを指定必要.

    pref12_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref12_name',to_field="prefecture")

    pref13_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref13_name',to_field="prefecture")

    pref14_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref14_name',to_field="prefecture")

    pref15_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref15_name',to_field="prefecture")

    pref16_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref16_name',to_field="prefecture")

    pref17_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref17_name',to_field="prefecture")

    pref18_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref18_name',to_field="prefecture")

    pref19_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref19_name',to_field="prefecture")

    pref20_name = models.ForeignKey(Prefectures, on_delete=models.DO_NOTHING, null=True,default=None,related_name='pref20_name',to_field="prefecture")    


    def __str__(self):
        return str(self.official_name) + ',' + str(self.pref1_name)
    class Meta:
        verbose_name = "Pref_ranks"
        verbose_name_plural = "Pref_ranks"  


class Frequentwords(models.Model): # パーティーション用

    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)    
    episode = models.PositiveSmallIntegerField(default=0,null=True)

    freq1 = models.CharField(null=True,max_length=15) # max10字
    freq1_count = models.PositiveIntegerField(default=0,null=True) #integral field(0〜2147483647 
    freq2 = models.CharField(null=True,max_length=15)
    freq2_count = models.PositiveIntegerField(default=0,null=True)
    freq3 = models.CharField(null=True,max_length=15)
    freq3_count = models.PositiveIntegerField(default=0,null=True)    
    freq4 = models.CharField(null=True,max_length=15)
    freq4_count = models.PositiveIntegerField(default=0,null=True) 
    freq5 = models.CharField(null=True,max_length=15)
    freq5_count = models.PositiveIntegerField(default=0,null=True)
    freq6 = models.CharField(null=True,max_length=15)
    freq6_count = models.PositiveIntegerField(default=0,null=True)
    freq7 = models.CharField(null=True,max_length=15)
    freq7_count = models.PositiveIntegerField(default=0,null=True)
    freq8 = models.CharField(null=True,max_length=15)
    freq8_count = models.PositiveIntegerField(default=0,null=True)
    freq9 = models.CharField(null=True,max_length=15)
    freq9_count = models.PositiveIntegerField(default=0,null=True)
    freq10 = models.CharField(null=True,max_length=15)
    freq10_count = models.PositiveIntegerField(default=0,null=True)
    
    freq11 = models.CharField(null=True,max_length=15) # max10字
    freq11_count = models.PositiveIntegerField(default=0,null=True)
    freq12 = models.CharField(null=True,max_length=15)
    freq12_count = models.PositiveIntegerField(default=0,null=True)
    freq13 = models.CharField(null=True,max_length=15)
    freq13_count = models.PositiveIntegerField(default=0,null=True)
    freq14 = models.CharField(null=True,max_length=15)
    freq14_count = models.PositiveIntegerField(default=0,null=True)
    freq15 = models.CharField(null=True,max_length=15)
    freq15_count = models.PositiveIntegerField(default=0,null=True)
    freq16 = models.CharField(null=True,max_length=15)
    freq16_count = models.PositiveIntegerField(default=0,null=True)
    freq17 = models.CharField(null=True,max_length=15)
    freq17_count = models.PositiveIntegerField(default=0,null=True)
    freq18 = models.CharField(null=True,max_length=15)
    freq18_count = models.PositiveIntegerField(default=0,null=True)
    freq19 = models.CharField(null=True,max_length=15)
    freq19_count = models.PositiveIntegerField(default=0,null=True)
    freq20 = models.CharField(null=True,max_length=15)
    freq20_count = models.PositiveIntegerField(default=0,null=True)
    
    freq21 = models.CharField(null=True,max_length=15) # max10字
    freq21_count = models.PositiveIntegerField(default=0,null=True)
    freq22 = models.CharField(null=True,max_length=15)
    freq22_count = models.PositiveIntegerField(default=0,null=True)
    freq23 = models.CharField(null=True,max_length=15)
    freq23_count = models.PositiveIntegerField(default=0,null=True)    
    freq24 = models.CharField(null=True,max_length=15)
    freq24_count = models.PositiveIntegerField(default=0,null=True) 
    freq25 = models.CharField(null=True,max_length=15)
    freq25_count = models.PositiveIntegerField(default=0,null=True)
    freq26 = models.CharField(null=True,max_length=15)
    freq26_count = models.PositiveIntegerField(default=0,null=True)
    freq27 = models.CharField(null=True,max_length=15)
    freq27_count = models.PositiveIntegerField(default=0,null=True)
    freq28 = models.CharField(null=True,max_length=15)
    freq28_count = models.PositiveIntegerField(default=0,null=True)
    freq29 = models.CharField(null=True,max_length=15)
    freq29_count = models.PositiveIntegerField(default=0,null=True)
    freq30 = models.CharField(null=True,max_length=15)
    freq30_count = models.PositiveIntegerField(default=0,null=True)
    
    freq31 = models.CharField(null=True,max_length=15) # max10字
    freq31_count = models.PositiveIntegerField(default=0,null=True)
    freq32 = models.CharField(null=True,max_length=15)
    freq32_count = models.PositiveIntegerField(default=0,null=True)
    freq33 = models.CharField(null=True,max_length=15)
    freq33_count = models.PositiveIntegerField(default=0,null=True)    
    freq34 = models.CharField(null=True,max_length=15)
    freq34_count = models.PositiveIntegerField(default=0,null=True) 
    freq35 = models.CharField(null=True,max_length=15)
    freq35_count = models.PositiveIntegerField(default=0,null=True)
    freq36 = models.CharField(null=True,max_length=15)
    freq36_count = models.PositiveIntegerField(default=0,null=True)
    freq37 = models.CharField(null=True,max_length=15)
    freq37_count = models.PositiveIntegerField(default=0,null=True)
    freq38 = models.CharField(null=True,max_length=15)
    freq38_count = models.PositiveIntegerField(default=0,null=True)
    freq39 = models.CharField(null=True,max_length=15)
    freq39_count = models.PositiveIntegerField(default=0,null=True)
    freq40 = models.CharField(null=True,max_length=15)
    freq40_count = models.PositiveIntegerField(default=0,null=True)
    
    freq41 = models.CharField(null=True,max_length=15) # max10字
    freq41_count = models.PositiveIntegerField(default=0,null=True)
    freq42 = models.CharField(null=True,max_length=15)
    freq42_count = models.PositiveIntegerField(default=0,null=True)
    freq43 = models.CharField(null=True,max_length=15)
    freq43_count = models.PositiveIntegerField(default=0,null=True)    
    freq44 = models.CharField(null=True,max_length=15)
    freq44_count = models.PositiveIntegerField(default=0,null=True) 
    freq45 = models.CharField(null=True,max_length=15)
    freq45_count = models.PositiveIntegerField(default=0,null=True)
    freq46 = models.CharField(null=True,max_length=15)
    freq46_count = models.PositiveIntegerField(default=0,null=True)
    freq47 = models.CharField(null=True,max_length=15)
    freq47_count = models.PositiveIntegerField(default=0,null=True)
    freq48 = models.CharField(null=True,max_length=15)
    freq48_count = models.PositiveIntegerField(default=0,null=True)
    freq49 = models.CharField(null=True,max_length=15)
    freq49_count = models.PositiveIntegerField(default=0,null=True)
    freq50 = models.CharField(null=True,max_length=15)
    freq50_count = models.PositiveIntegerField(default=0,null=True)


    def __str__(self):
        return str(self.official_name) + ',' + str(self.freq1)

    class Meta:
        verbose_name = "Frequentwords"
        verbose_name_plural = "Frequentwords"  

        
class Longevents(models.Model): # パーティーション用


    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)
    url =models.URLField(null=True)
    date_s = models.DateTimeField(null=True)
    date_e = models.DateTimeField(null=True)
    time_s = models.CharField(null=True,max_length=5) # ex.18:00
    time_e = models.CharField(null=True,max_length=5)
    weekday = models.CharField(null=True,max_length=5) # ex.'火,日' 複数時はカンマ区切り
    media = models.CharField(null=True,max_length=2) # ex.'tv'
    channel = models.CharField(null=True,max_length=10) # ex.'東京テレビ他'
    title = models.CharField(null=True,max_length=40) # 鬼滅ラジオ
    

    
    def __str__(self):
        return '<'+str(self.official_name)+','+str(self.program_title) +'>'

    class Meta:
        verbose_name = "Longevents"
        verbose_name_plural = "Longevents" 


class Abouts(models.Model): # パーティーション用


    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)

    story = models.CharField(null=True,max_length=300) # あらすじ
    
    p_soukatsu = models.CharField(null=True,max_length=800) # summary総括
    n_soukatsu = models.CharField(null=True,max_length=400) # summary総括

    def __str__(self):
        return '<'+str(self.official_name)+','+str(self.story) +'>'

    class Meta:
        verbose_name = "Abouts"
        verbose_name_plural = "Abouts" 
        

class Oadates(models.Model): # パーティーション用


    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)

    episode1 = models.DateTimeField(null=True)
    episode2 = models.DateTimeField(null=True)
    episode3 = models.DateTimeField(null=True)
    episode4 = models.DateTimeField(null=True)
    episode5 = models.DateTimeField(null=True)
    episode6 = models.DateTimeField(null=True)
    episode7 = models.DateTimeField(null=True)
    episode8 = models.DateTimeField(null=True)
    episode9 = models.DateTimeField(null=True)
    episode10 = models.DateTimeField(null=True)
    episode11 = models.DateTimeField(null=True)
    episode12 = models.DateTimeField(null=True)
    episode13 = models.DateTimeField(null=True)
    episode14 = models.DateTimeField(null=True)
    episode15 = models.DateTimeField(null=True)
    episode16 = models.DateTimeField(null=True)
    episode17 = models.DateTimeField(null=True)
    episode18 = models.DateTimeField(null=True)
    episode19 = models.DateTimeField(null=True)    
    episode20 = models.DateTimeField(null=True)    
    episode21 = models.DateTimeField(null=True)
    episode22 = models.DateTimeField(null=True)
    episode23 = models.DateTimeField(null=True)
    episode24 = models.DateTimeField(null=True)
    episode25 = models.DateTimeField(null=True)
    episode26 = models.DateTimeField(null=True)
    episode27 = models.DateTimeField(null=True)
    episode28 = models.DateTimeField(null=True)
    episode29 = models.DateTimeField(null=True)
    episode30 = models.DateTimeField(null=True)
 
    episode_title1 = models.CharField(null=True,max_length=50)
    episode_title2 = models.CharField(null=True,max_length=50)
    episode_title3 = models.CharField(null=True,max_length=50)
    episode_title4 = models.CharField(null=True,max_length=50)
    episode_title5 = models.CharField(null=True,max_length=50)
    episode_title6 = models.CharField(null=True,max_length=50)
    episode_title7 = models.CharField(null=True,max_length=50)
    episode_title8 = models.CharField(null=True,max_length=50)
    episode_title9 = models.CharField(null=True,max_length=50)
    episode_title10 = models.CharField(null=True,max_length=50)
    episode_title11 = models.CharField(null=True,max_length=50)
    episode_title12 = models.CharField(null=True,max_length=50)
    episode_title13 = models.CharField(null=True,max_length=50)
    episode_title14 = models.CharField(null=True,max_length=50)
    episode_title15 = models.CharField(null=True,max_length=50)
    episode_title16 = models.CharField(null=True,max_length=50)
    episode_title17 = models.CharField(null=True,max_length=50)
    episode_title18 = models.CharField(null=True,max_length=50)    
    episode_title19 = models.CharField(null=True,max_length=50)
    episode_title20 = models.CharField(null=True,max_length=50)
    episode_title21 = models.CharField(null=True,max_length=50)
    episode_title22 = models.CharField(null=True,max_length=50)
    episode_title23 = models.CharField(null=True,max_length=50)
    episode_title24 = models.CharField(null=True,max_length=50)
    episode_title25 = models.CharField(null=True,max_length=50)
    episode_title26 = models.CharField(null=True,max_length=50)
    episode_title27 = models.CharField(null=True,max_length=50)
    episode_title28 = models.CharField(null=True,max_length=50)
    episode_title29 = models.CharField(null=True,max_length=50)
    episode_title30 = models.CharField(null=True,max_length=50)
    
    title_tag1 = models.CharField(null=True,max_length=50)
    title_tag2 = models.CharField(null=True,max_length=50)
    title_tag3 = models.CharField(null=True,max_length=50)
    title_tag4 = models.CharField(null=True,max_length=50)
    title_tag5 = models.CharField(null=True,max_length=50)
    title_tag6 = models.CharField(null=True,max_length=50)
    title_tag7 = models.CharField(null=True,max_length=50)
    title_tag8 = models.CharField(null=True,max_length=50)
    title_tag9 = models.CharField(null=True,max_length=50)
    title_tag10 = models.CharField(null=True,max_length=50)
    title_tag11 = models.CharField(null=True,max_length=50)
    title_tag12 = models.CharField(null=True,max_length=50)
    title_tag13 = models.CharField(null=True,max_length=50)
    title_tag14 = models.CharField(null=True,max_length=50)
    title_tag15 = models.CharField(null=True,max_length=50)
    title_tag16 = models.CharField(null=True,max_length=50)
    title_tag17 = models.CharField(null=True,max_length=50)
    title_tag18 = models.CharField(null=True,max_length=50)
    title_tag19 = models.CharField(null=True,max_length=50)
    title_tag20 = models.CharField(null=True,max_length=50)
    title_tag21 = models.CharField(null=True,max_length=50)
    title_tag22 = models.CharField(null=True,max_length=50)
    title_tag23 = models.CharField(null=True,max_length=50)
    title_tag24 = models.CharField(null=True,max_length=50)
    title_tag25 = models.CharField(null=True,max_length=50)
    title_tag26 = models.CharField(null=True,max_length=50)
    title_tag27 = models.CharField(null=True,max_length=50)
    title_tag28 = models.CharField(null=True,max_length=50)
    title_tag29 = models.CharField(null=True,max_length=50)
    title_tag30 = models.CharField(null=True,max_length=50)
    

    outline1 = models.CharField(null=True,max_length=1000)
    outline2 = models.CharField(null=True,max_length=1000)
    outline3 = models.CharField(null=True,max_length=1000)
    outline4 = models.CharField(null=True,max_length=1000)
    outline5 = models.CharField(null=True,max_length=1000)
    outline6 = models.CharField(null=True,max_length=1000)
    outline7 = models.CharField(null=True,max_length=1000)
    outline8 = models.CharField(null=True,max_length=1000)
    outline9 = models.CharField(null=True,max_length=1000)
    outline10 = models.CharField(null=True,max_length=1000)
    outline11 = models.CharField(null=True,max_length=1000)
    outline12 = models.CharField(null=True,max_length=1000)
    outline13 = models.CharField(null=True,max_length=1000)
    outline14 = models.CharField(null=True,max_length=1000)
    outline15 = models.CharField(null=True,max_length=1000)
    outline16 = models.CharField(null=True,max_length=1000)
    outline17 = models.CharField(null=True,max_length=1000)
    outline18 = models.CharField(null=True,max_length=1000)
    outline19 = models.CharField(null=True,max_length=1000)
    outline20 = models.CharField(null=True,max_length=1000)
    outline21 = models.CharField(null=True,max_length=1000)
    outline22 = models.CharField(null=True,max_length=1000)
    outline23 = models.CharField(null=True,max_length=1000)
    outline24 = models.CharField(null=True,max_length=1000)
    outline25 = models.CharField(null=True,max_length=1000)
    outline26 = models.CharField(null=True,max_length=1000)
    outline27 = models.CharField(null=True,max_length=1000)
    outline28 = models.CharField(null=True,max_length=1000)
    outline29 = models.CharField(null=True,max_length=1000)
    outline30 = models.CharField(null=True,max_length=1000)

    def __str__(self):
        return '<'+str(self.official_name) +'>'

    class Meta:
        verbose_name = "Oadates"
        verbose_name_plural = "Oadates"


class Fanarts(models.Model): # パーティーション用

    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)
    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)
    episode = models.PositiveSmallIntegerField(default=0,null=True)
    
    s_date = models.DateTimeField(null=True)# 作成した日時
    e_date = models.DateTimeField(null=True)

    fan_art1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art1')
    fan_art2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art2')
    fan_art3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art3')
    fan_art4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art4')
    fan_art5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art5')
    fan_art6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art6')
    fan_art7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art7')
    fan_art8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art8')
    fan_art9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art9')
    fan_art10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art10')

    fan_art11 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art11')
    fan_art12 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art12')
    fan_art13 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art13')
    fan_art14 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art14')
    fan_art15 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art15')
    fan_art16 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art16')
    fan_art17 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art17')
    fan_art18 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art18')
    fan_art19 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art19')
    fan_art20 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art20')

    fan_art21 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art21')
    fan_art22 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art22')
    fan_art23 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art23')
    fan_art24 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art24')
    fan_art25 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art25')
    fan_art26 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art26')
    fan_art27 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art27')
    fan_art28 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art28')
    fan_art29 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art29')
    fan_art30 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='fan_art30')

    def __str__(self):
        return '<'+str(self.official_name)+','+str(self.episode) +'>'

    class Meta:
        verbose_name = "Fanarts"
        verbose_name_plural = "Fanarts"


class Quiz(models.Model): # パーティーション用

    official_name = models.ForeignKey(Official_names, on_delete=models.SET_DEFAULT,default=0)
    level = models.PositiveSmallIntegerField(default=1,null=True)
    kind = models.PositiveSmallIntegerField(default=0,null=True)
    q_1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_1')
    q_2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_2')
    q_3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_3')
    q_4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_4')
    q_5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_5')
    q_6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_6')
    q_7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_7')
    q_8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_8')
    q_9 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_9')
    q_10 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_10')

    q_11 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_11')
    q_12 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_12')
    q_13 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_13')
    q_14 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_14')
    q_15 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_15')
    q_16 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_16')
    q_17 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_17')
    q_18 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_18')
    q_19 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_19')
    q_20 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_20')

    q_21 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_21')
    q_22 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_22')
    q_23 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_23')
    q_24 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_24')
    q_25 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_25')
    q_26 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_26')
    q_27 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_27')
    q_28 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_28')
    q_29 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_29')
    q_30 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='q_30')

    def __str__(self):
        return '<'+str(self.official_name)+','+str(self.q_1) +'>'

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"


class Categorys(models.Model):
    
    post = models.SlugField(unique=True,null=True) # official_name-episode(0001023-021)

# category1
    name_c1 = models.CharField(max_length=100, default='カテゴリー1')
    p2count_c1 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c1 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c1 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c1 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c1')
    p2data2_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c1')
    p2data3_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c1')
    p2data4_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c1')
    p2data5_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c1')

    p1data1_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c1')
    p1data2_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c1')
    p1data3_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c1')
    p1data4_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c1')
    p1data5_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c1')

    n1data1_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c1')
    n1data2_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c1')
    n1data3_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c1')
    n1data4_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c1')
    n1data5_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c1')

    n2data1_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c1')
    n2data2_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c1')
    n2data3_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c1')
    n2data4_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c1')
    n2data5_c1 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c1')

    freqs_c1 = models.TextField(default=None,null=True)
    keys_c1 = models.CharField(max_length=100, default='') # 'a,b,c d..' 空白がand条件,カンマがor条件
#category2
    name_c2 = models.CharField(max_length=100, default='カテゴリー2')
    p2count_c2 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c2 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c2 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c2 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c2')
    p2data2_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c2')
    p2data3_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c2')
    p2data4_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c2')
    p2data5_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c2')

    p1data1_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c2')
    p1data2_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c2')
    p1data3_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c2')
    p1data4_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c2')
    p1data5_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c2')

    n1data1_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c2')
    n1data2_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c2')
    n1data3_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c2')
    n1data4_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c2')
    n1data5_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c2')

    n2data1_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c2')
    n2data2_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c2')
    n2data3_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c2')
    n2data4_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c2')
    n2data5_c2 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c2')

    freqs_c2 = models.TextField(default=None,null=True)
    keys_c2 = models.CharField(max_length=100, default='')
#category3
    name_c3 = models.CharField(max_length=100, default='カテゴリー3')
    p2count_c3 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c3 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c3 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c3 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c3')
    p2data2_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c3')
    p2data3_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c3')
    p2data4_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c3')
    p2data5_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c3')

    p1data1_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c3')
    p1data2_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c3')
    p1data3_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c3')
    p1data4_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c3')
    p1data5_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c3')

    n1data1_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c3')
    n1data2_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c3')
    n1data3_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c3')
    n1data4_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c3')
    n1data5_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c3')

    n2data1_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c3')
    n2data2_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c3')
    n2data3_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c3')
    n2data4_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c3')
    n2data5_c3 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c3')

    freqs_c3 = models.TextField(default=None,null=True)
    keys_c3 = models.CharField(max_length=100, default='')    
#category4
    name_c4 = models.CharField(max_length=100, default='カテゴリー4')
    p2count_c4 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c4 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c4 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c4 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c4')
    p2data2_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c4')
    p2data3_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c4')
    p2data4_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c4')
    p2data5_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c4')

    p1data1_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c4')
    p1data2_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c4')
    p1data3_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c4')
    p1data4_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c4')
    p1data5_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c4')

    n1data1_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c4')
    n1data2_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c4')
    n1data3_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c4')
    n1data4_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c4')
    n1data5_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c4')

    n2data1_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c4')
    n2data2_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c4')
    n2data3_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c4')
    n2data4_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c4')
    n2data5_c4 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c4')

    freqs_c4 = models.TextField(default=None,null=True)
    keys_c4 = models.CharField(max_length=100, default='') 
#category5
    name_c5 = models.CharField(max_length=100, default='カテゴリー5')
    p2count_c5 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c5 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c5 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c5 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c5')
    p2data2_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c5')
    p2data3_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c5')
    p2data4_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c5')
    p2data5_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c5')

    p1data1_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c5')
    p1data2_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c5')
    p1data3_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c5')
    p1data4_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c5')
    p1data5_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c5')

    n1data1_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c5')
    n1data2_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c5')
    n1data3_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c5')
    n1data4_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c5')
    n1data5_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c5')

    n2data1_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c5')
    n2data2_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c5')
    n2data3_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c5')
    n2data4_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c5')
    n2data5_c5 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c5')

    freqs_c5 = models.TextField(default=None,null=True)
    keys_c5 = models.CharField(max_length=100, default='')    

#category6
    name_c6 = models.CharField(max_length=100, default='カテゴリー6')
    p2count_c6 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c6 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c6 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c6 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c6')
    p2data2_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c6')
    p2data3_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c6')
    p2data4_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c6')
    p2data5_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c6')

    p1data1_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c6')
    p1data2_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c6')
    p1data3_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c6')
    p1data4_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c6')
    p1data5_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c6')

    n1data1_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c6')
    n1data2_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c6')
    n1data3_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c6')
    n1data4_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c6')
    n1data5_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c6')

    n2data1_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c6')
    n2data2_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c6')
    n2data3_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c6')
    n2data4_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c6')
    n2data5_c6 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c6')

    freqs_c6 = models.TextField(default=None,null=True)
    keys_c6 = models.CharField(max_length=100, default='')    
    
#category7
    name_c7 = models.CharField(max_length=100, default='カテゴリー7')
    p2count_c7 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c7 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c7 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c7 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c7')
    p2data2_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c7')
    p2data3_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c7')
    p2data4_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c7')
    p2data5_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c7')

    p1data1_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c7')
    p1data2_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c7')
    p1data3_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c7')
    p1data4_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c7')
    p1data5_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c7')

    n1data1_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c7')
    n1data2_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c7')
    n1data3_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c7')
    n1data4_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c7')
    n1data5_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c7')

    n2data1_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c7')
    n2data2_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c7')
    n2data3_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c7')
    n2data4_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c7')
    n2data5_c7 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c7')

    freqs_c7 = models.TextField(default=None,null=True)
    keys_c7 = models.CharField(max_length=100, default='')    

#category8
    name_c8 = models.CharField(max_length=100, default='カテゴリー8')
    p2count_c8 = models.PositiveSmallIntegerField(default=0,null=True)
    p1count_c8 = models.PositiveSmallIntegerField(default=0,null=True)
    n1count_c8 = models.PositiveSmallIntegerField(default=0,null=True)
    n2count_c8 = models.PositiveSmallIntegerField(default=0,null=True)

    p2data1_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data1_c8')
    p2data2_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data2_c8')
    p2data3_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data3_c8')
    p2data4_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data4_c8')
    p2data5_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p2data5_c8')

    p1data1_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data1_c8')
    p1data2_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data2_c8')
    p1data3_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data3_c8')
    p1data4_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data4_c8')
    p1data5_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='p1data5_c8')

    n1data1_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data1_c8')
    n1data2_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data2_c8')
    n1data3_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data3_c8')
    n1data4_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data4_c8')
    n1data5_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n1data5_c8')

    n2data1_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data1_c8')
    n2data2_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data2_c8')
    n2data3_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data3_c8')
    n2data4_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data4_c8')
    n2data5_c8 = models.ForeignKey(Tweetdata2, on_delete=models.DO_NOTHING, null=True,default=None,related_name='n2data5_c8')

    freqs_c8 = models.TextField(default=None,null=True)
    keys_c8 = models.CharField(max_length=100, default='')

    def __str__(self):
        return '<'+str(self.post)+','+str(self.freqs1_c1) +'>'

    class Meta:
        verbose_name = "Categorys"
        verbose_name_plural = "Categorys"


class Comment(models.Model):
    
    user_name = models.CharField('名前', max_length=100, default='名無し')
    message = models.TextField('本文')
    parent=models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    target = models.SlugField(null=True) # official_name-episode(0001023-021)
    
    created = models.DateTimeField('作成日', default=timezone.now)
    updated = models.DateTimeField('更新日', default=timezone.now)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        return self.message
    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)
