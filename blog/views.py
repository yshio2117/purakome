from django.shortcuts import render
from django.views import generic
from .models import Blog
# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "blog_index.html"
    
def tech_detail(request,blog_id):
    
    if request.method == 'POST':
        
        blog = Blog.objects.get(id=blog_id)
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,

            }
    elif request.method == 'GET':
        blog = Blog.objects.get(id=blog_id)
        print(blog.title_tag)
        params = {
            'blog':blog,        
            'title_tag':blog.title_tag.split(',') if blog.title_tag else None,
            }
        
    return render(request, 'tech_detail.html', params)        

