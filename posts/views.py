from django.http import HttpResponse
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
    commentform = CommentCreateForm()
    replyform = ReplyCreateForm()

    context = {
        'post' : post,
        'commentform' : commentform,
        'replyform' : replyform,   
    }

    return render(request, 'posts/post_page.html', context)

@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid:
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post
            comment.save()
    
    return redirect('post', post.id)

@login_required
def comment_delete_view(request, pk):
    post = get_object_or_404(Comment, id=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Comment deleted')
        return redirect('post', post.parent_post.id)

    return render(request, 'posts/comment_delete.html', {'comment':post})

@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)

    if request.method == 'POST':
        form = ReplyCreateForm(request.POST)
        if form.is_valid:
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_post = comment
            reply.save()
    
    return redirect('post', comment.parent_post.id)


@login_required
def reply_delete_view(request, pk):
    reply = get_object_or_404(Reply, id=pk, author=request.user)
    
    if request.method == 'POST':
        reply.delete()
        messages.success(request, 'Reply deleted')
        return redirect('post', reply.parent_comment.parent_post.id)

    return render(request, 'posts/reply_delete.html', {'reply':reply})

# decorators explanation https://youtu.be/UOOMn0PeIWM?list=PL5E1F5cTSTtTAIw_lBp1hE8nAKfCXgUpW&t=537
# skeleton of a decorator
# def like_toggle(model):
#     def inner_func(func):
#         def wrapper(request, *args, **kwargs):
#             ...
#             return func(request, *args, **kwargs)
#         return wrapper
#     return inner_func

# decorator declaration
def like_toggle(model):
    def inner_func(func):
        def wrapper(request, *args, **kwargs):
            post = get_object_or_404(model, id=kwargs.get('pk'))
            user_exist = post.likes.filter(username=request.user.username).exists()

            if post.author != request.user:
                if user_exist:
                    post.likes.remove(request.user)
                else:
                    post.likes.add(request.user)
            return func(request, post)
        return wrapper
    return inner_func


@login_required
@like_toggle(Post)
def like_post(request, post):
    return render(request, 'snippets/likes.html', {'post':post})


@login_required
@like_toggle(Comment)
def like_comment(request, post):
    return render(request, 'snippets/likes_comment.html', {'comment':post})


@login_required
@like_toggle(Reply)
def like_reply(request, post):
    return render(request, 'snippets/likes_reply.html', {'reply':post})


# htmx added here during lesson 13 https://youtu.be/IxGcvqfI_iA?list=PL5E1F5cTSTtTAIw_lBp1hE8nAKfCXgUpW&t=1136
# this was how it looked before we modified it in lesson 14 to use a decorator.
# def like_post(request, pk):
    # post = get_object_or_404(Post, id=pk)
    # user_exist = post.likes.filter(username=request.user.username).exists()

    # if post.author != request.user:
    #     if user_exist:
    #         post.likes.remove(request.user)
    #     else:
    #         post.likes.add(request.user)

#     return render(request, 'snippets/likes.html', {'post':post})

# This is how like_comment would be implemented if it were duplicated from like_post
# def like_comment(request, pk):
#     comment = get_object_or_404(Comment, id=pk)
#     user_exist = comment.likes.filter(username=request.user.username).exists()

#     if comment.author != request.user:
#         if user_exist:
#             comment.likes.remove(request.user)
#         else:
#             comment.likes.add(request.user)

#     return render(request, 'snippets/likes.html', {'comment':comment})

