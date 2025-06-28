from django.contrib import admin
from django.urls import path
from .views.posts import home_view, post_create_view, post_delete_view, post_edit_view, post_page_view, comment_sent, reply_sent,comment_delete_view, reply_delete_view, like_post_view, like_comment_view, like_reply_view
urlpatterns = [
    path("", home_view, name="home"),
    path("tag/<slug:tag>/", home_view, name="home-tag"),
    path("post/create/", post_create_view, name="post-create"),
    path("post/<pk>/delete/", post_delete_view, name="post-delete"),
    path("post/<pk>/edit/", post_edit_view, name="post-edit"),
    path("post/<pk>/", post_page_view, name="post"),
    path("post/<pk>/like/", like_post_view, name="post-like"),
    path("post/<pk>/comment/send/", comment_sent, name="comment-sent"),
    path("comment/<pk>/like/", like_comment_view, name="comment-like"),
    path("comment/<pk>/reply/send/", reply_sent, name="reply-sent"),
    path("comment/<pk>/delete/", comment_delete_view, name="comment-delete"),
    path("reply/<pk>/like/", like_reply_view, name="reply-like"),
    path("reply/<pk>/delete", reply_delete_view, name="reply-delete"),
]
