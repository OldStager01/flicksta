"""
URL configuration for flicksta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("theboss/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("", include("f_posts.urls")),
    path("profile/", include("f_users.urls")),
]

# Only serve media files locally during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)