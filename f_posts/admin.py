from django.contrib import admin
from .models import Post, Tag, Comment, Reply, LikedPost, LikedComment
# Register your models here.
admin.site.site_header = "Flicksta Admin"
admin.site.site_title = "Flicksta Admin Portal"
admin.site.index_title = "Welcome to Flicksta Admin"

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(LikedPost)
admin.site.register(LikedComment)