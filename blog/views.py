from django.shortcuts import render
from django.views import generic
from .models import Blog
# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "blog_index.html"




def anime_detail(request,blog_id):
    
       
    if request.method == 'POST':
        
        blog = Blog.objects.get(id=blog_id)
        latest_article = Blog.objects.filter(category=blog.category).order_by('created_at').reverse()[:5]
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,
            'latest_article':latest_article,
            }
    elif request.method == 'GET':
        blog = Blog.objects.get(id=blog_id)
        #print(blog.title_tag)
        latest_article = Blog.objects.filter(category=blog.category).order_by('created_at').reverse()[:5]
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,
            'latest_article':latest_article,
            }

    return render(request, 'tech_detail.html', params)        
   

def tech_detail(request,blog_id):
    
       
    if request.method == 'POST':
        
        blog = Blog.objects.get(id=blog_id)
        latest_article = Blog.objects.filter(category=blog.category).order_by('created_at').reverse()[:5]
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,
            'latest_article':latest_article,
            }
    elif request.method == 'GET':
        blog = Blog.objects.get(id=blog_id)
        #print(blog.title_tag)
        latest_article = Blog.objects.filter(category=blog.category).order_by('created_at').reverse()[:5]
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,
            'latest_article':latest_article,
            }

    return render(request, 'tech_detail.html', params)        

