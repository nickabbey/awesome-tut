from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.contrib import messages
from django import forms
from .models import Post
from .forms import *
from bs4 import BeautifulSoup
import requests


def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
    
    categories = Tag.objects.all()

    context = {
        'posts' : posts,
        'categories' : categories,
        'tag' : tag,
    }

    return render(request, 'posts/home.html', context)
    
@login_required   
def post_create_view(request):
    form = PostCreateForm()

    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)

            # web scrape
            website = requests.get(form.data['url'])
            sourcecode = BeautifulSoup(website.text, 'html.parser')
            # looking at html source on flicker shows that the images themseles are always served from this domain
            find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            # find_image returns a list of lists. so we grab the first item in the list, which is a list, and form that list, we grab the value of the 'content' item
            image = find_image[0]['content']
            # assign the image url we just found to the image property of the post
            post.image = image
            # similarly, titles are always in a header names photo-title
            find_title = sourcecode.select('h1.photo-title')
            # and we need to process that slightly before we use it. We grab the first element that matched the sourcecode query and convert it to text
            title = find_title[0].text.strip()
            post.title = title
            # the artist is under anchor elements stored as owner-name
            find_artist = sourcecode.select('a.owner-name')
            # like title, convert the first item in the list to text
            artist = find_artist[0].text.strip()
            post.artist = artist
            
            post.author = request.user

            post.save()
            form.save_m2m()
            return redirect('home')

    return render(request, 'posts/post_create.html', {'form':form})

@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted')
        return redirect('home')

    return render(request, 'posts/post_delete.html', {'post':post})

@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk, author=request.user)
    form = PostEditForm(instance=post)

    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated')
            return redirect('home')
        
    context = {
        'post':post,
        'form':form
    }
    return render(request, 'posts/post_edit.html', context)

def post_page_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    return render(request, 'posts/post_page.html', {'post': post})
