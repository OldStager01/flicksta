from django import forms
from .models import Post, Comment, Reply

class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['url', 'body', 'tags']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter flickr image URL'}),
            'body': forms.Textarea(attrs={'class': 'form-control font1 text-4xl ', 'rows': 3, 'placeholder': 'Enter post content'}),
            'tags': forms.CheckboxSelectMultiple()
        }
        labels = {
            'url': 'URL',
            'body': 'Caption',
            'tags': 'Tags',
        }
        
class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body', 'tags']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control font1 text-4xl ', 'rows': 3, 'placeholder': 'Enter post content'}),
            'tags': forms.CheckboxSelectMultiple()
            
        }
        labels = {
            'body': 'Caption',
            'tags': 'Tags',
        }
        
        
class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your comment here...'
            })
        }
        labels = {
            'body': 'Comment'
        }

class ReplyCreateForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Enter your reply here...'
            })
        }
        labels = {
            'body': 'Reply'
        }