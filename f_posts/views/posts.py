from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from django.core.paginator import Paginator
from ..models import Post, Tag, Comment, Reply
from ..forms import PostCreateForm, PostEditForm, CommentCreateForm, ReplyCreateForm
from bs4 import BeautifulSoup
from f_features.views import feature_enabled
import requests

def home_view(request, tag = None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
        
    paginator = Paginator(posts, 3)
    page = int(request.GET.get('page',1))
    try:
        posts = paginator.get_page(page)
    except Exception as e:
        messages.error(request, 'Invalid page number.')
        return HttpResponse("")
    
    feature_herobutton = feature_enabled(1)
    
    context = {
        'posts': posts,
        'tag': tag,
        'page': page,
        'feature_herobutton': feature_herobutton,
    }
    
    if request.htmx:
        return render(request, 'f_posts/snippets/loop_homepage_posts.html', context)
    return render(request, 'f_posts/home.html', context)

@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            url = post.url
            if url:
                try:
                    website = requests.get(url)
                    source_code = BeautifulSoup(website.text, 'html.parser')
                    
                    find_image = source_code.select('meta[content^="https://live.staticflickr.com/"]')
                    image = find_image[0]['content'] if find_image else None
                    post.image = image
                    
                    find_title = source_code.select('h1.photo-title')
                    title = find_title[0].text.strip() if find_title else None
                    post.title = title
                    
                    find_artist = source_code.select('a.owner-name')
                    artist = find_artist[0].text.strip() if find_artist else None
                    post.artist = artist
                    
                    post.author = request.user
                    
                except Exception as e:
                    print(f"Error fetching data from URL: {e}")
                    post.image = None
                    post.title = None
                    post.artist = None
            post.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = PostCreateForm()
    return render(request, 'f_posts/post_create.html', {'form': form})

@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('home')
    return render(request, 'f_posts/post_delete.html', {'post': post})

@login_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('home')
    else:
        form = PostEditForm(instance=post)
        
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'f_posts/post_edit.html', context)

def post_page_view(request, pk):
    post = get_object_or_404(Post, pk=pk)

    commentform = CommentCreateForm()
    replyform = ReplyCreateForm()

    if request.htmx:
        if 'top' in request.GET:
            comments = post.comments.annotate(like_count=Count('likes')).filter(like_count__gt=0).order_by('-like_count')
        else:
            comments = post.comments.all()
        return render(request, 'f_posts/snippets/loop_postpage_comments.html', {'comments': comments, 'replyform': replyform})

    context = {
        'post': post,
        'commentform': commentform,
        'replyform': replyform
    }
    return render(request, 'f_posts/post_page.html', context)

@login_required
def comment_sent(request, pk):
    post = get_object_or_404(Post, id=pk)
    
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.parent_post = post            
            comment.save()

    return render(request, 'f_posts/snippets/add_comment.html', {'comment': comment, 'post': post})

@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    replyform = ReplyCreateForm()
    if request.method == 'POST':
        form = ReplyCreateForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent_comment = comment
            reply.save()

    return render(request, 'f_posts/snippets/add_reply.html', {'reply': reply, 'comment': comment, 'replyform': replyform})

@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    if request.method == 'POST':
        parent_post = comment.parent_post
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('post', pk=parent_post.pk)
    return render(request, 'f_posts/post_comment_delete.html', {'post': comment.parent_post, 'comment': comment })

@login_required
def reply_delete_view(request, pk):
    reply = get_object_or_404(Reply, pk=pk, author=request.user)
    if request.method == 'POST':
        parent_comment = reply.parent_comment
        reply.delete()
        messages.success(request, 'Reply deleted successfully.')
        return redirect('post', pk=reply.parent_comment.parent_post.id)
    return render(request, 'f_posts/post_reply_delete.html', {'reply': reply })

def like_toggle(model):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            pk = kwargs.get('pk')
            if not pk:
                return HttpResponse("Post ID is required.", status=400)
            instance = get_object_or_404(model, pk=pk)
            if instance.author == request.user:
                messages.error(request, 'You cannot like your own post.')
                return redirect('post', pk=pk)

            user_exists = instance.likes.filter(id=request.user.id).exists()
            if user_exists:
                instance.likes.remove(request.user)
            else:
                instance.likes.add(request.user)
            return func(request, instance)
        return wrapper
    return decorator

@login_required
@like_toggle(Post)
def like_post_view(request, post):
    return render(request, 'f_posts/snippets/likes.html', {'post': post})

@login_required
@like_toggle(Comment)   
def like_comment_view(request, comment):
    return render(request, 'f_posts/snippets/likes_comment.html', {'comment': comment})

@login_required
@like_toggle(Reply)
def like_reply_view(request, reply):
    return render(request, 'f_posts/snippets/likes_reply.html', {'reply': reply})