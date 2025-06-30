"""
URL configuration for flicksta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from f_posts.sitemaps import StaticSitemap, CategorySitemap, PostPageSitemap
from django.views.generic import TemplateView

# Sitemaps
from django.contrib.sitemaps.views import sitemap
sitemaps ={
    'static': StaticSitemap,
    'categories': CategorySitemap,
    'postpages': PostPageSitemap,
}


urlpatterns = [
    path("sitemap.xml/", sitemap, {'sitemaps':sitemaps }, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt/", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots.txt"), 
    path("theboss/", admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("", include("f_posts.urls")),
    path("profile/", include("f_users.urls")),
    path("_/", include("f_landingpages.urls")),
]

# Only serve media files locally during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)