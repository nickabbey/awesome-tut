from django.shortcuts import render, redirect
from django.forms import ModelForm
from django import forms
from .models import Post
from bs4 import BeautifulSoup
import requests


def home_view(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts':posts})


class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['url', 'body']
        labels = {
            'body':'Caption',
        }
        widgets = {
            'body' : forms.Textarea(attrs={'rows':3, 'placeholder':'Add a caption ...', 'class': 'font1 text-4xl'}),
            'url' : forms.Textarea(attrs={'rows':1,'placeholder':'Add url...'}),
        }


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

            post.save()
            return redirect('home')

    return render(request, 'posts/post_create.html', {'form':form})
