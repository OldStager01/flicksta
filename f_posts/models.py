from django.db import models
from django.contrib.auth.models import User
import uuid
from cloudinary.models import CloudinaryField

class Post(models.Model):
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    url = models.URLField(max_length=2000, blank=True, null=True)
    image = models.URLField(max_length=2000)
    body = models.TextField()
    likes = models.ManyToManyField(User, through='LikedPost', related_name='likedposts', blank=True)   
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        ordering = ['-created_at']
        
        
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # image = models.FileField(upload_to='icons/', blank=True, null=True)
    image = CloudinaryField('image', folder="tags", null=True, blank=True, resource_type='auto')
    slug = models.SlugField(max_length=100, unique=True)
    order = models.IntegerField(default=0, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']
        
        
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_comments', through="LikedComment", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    def __str__(self):
        try:
            return f"{self.author.username} - {self.body[:20]}"
        except AttributeError:
            # In case the author is None (e.g., if the user was deleted)
            return f"unknown author - {self.body[:20]}"
            
    
    class Meta:
        ordering = ['-created_at']
        
class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='replies')
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_replies', through="LikedReply", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    def __str__(self):
        try:
            return f"{self.author.username} - {self.body[:20]}"
        except AttributeError:
            # In case the author is None (e.g., if the user was deleted)
            return f"unknown author - {self.body[:20]}"
            
    
    class Meta:
        ordering = ['-created_at']
        

class LikedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
    
class LikedComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    class Meta:
        unique_together = ('user', 'comment')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} liked {self.comment.body[:20]}"
    
class LikedReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    class Meta:
        unique_together = ('user', 'reply')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} liked {self.reply.body[:20]}"