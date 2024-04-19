from django.forms import ModelForm
from django import forms
from .models import *


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


class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        labels = {
            'body':'Caption',
        }
        widgets = {
            'body' : forms.Textarea(attrs={'rows':3, 'placeholder':'Add a caption ...', 'class': 'font1 text-4xl'}),
        }

