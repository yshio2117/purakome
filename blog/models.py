from django.db import models

# Create your models here.
class Blog(models.Model):
    
    title = models.CharField(verbose_name='タイトル',max_length=60)
    title_tag = models.CharField(verbose_name='タイトルタグ',max_length=60,blank=True,null=True)
    content = models.TextField(verbose_name='本文',blank=True,null=True)
    preview_image = models.ImageField(verbose_name='プレビューイメージ',upload_to='image/blog/preview_image',blank=True,null=True)
    thumbnail = models.ImageField(verbose_name='サムネイル',upload_to='image/blog/thumbnail',blank=True,null=True)

    created_at = models.DateTimeField(verbose_name='作成日時',auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='更新日時',auto_now=True)

    
    class Meta:
        verbose_name_plural = 'Blog'
        
    def __str__(self):
        return self.title
