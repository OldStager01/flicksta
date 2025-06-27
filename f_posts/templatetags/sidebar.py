from django.template import Library
from django.db.models import Count
from ..models import Tag, Post, Comment

register = Library()

@register.inclusion_tag('includes/sidebar.html')
def sidebar_view(tag=None, user=None):
    categories = Tag.objects.all()
    top_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]
    top_comments = Comment.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]
    if user and user.is_authenticated:
        for post in top_posts:
            post.user_liked = post.likes.filter(id=user.id).exists()
            print(f"Post ID: {post.id}, User Liked: {post.user_liked}")
    else:
        for post in top_posts:
            post.user_liked = False
            print(f"Post ID: {post.id}, User Liked: {post.user_liked}")
            

    return {
        'categories': categories,
        'tag': tag,
        'top_posts': top_posts,
        'top_comments': top_comments,
        'user': user,
    }
