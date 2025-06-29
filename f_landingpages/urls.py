from django.contrib import admin
from django.urls import path
from .views import maintenance_view, locked_view
urlpatterns = [
    path("maintenance/", maintenance_view, name="maintenance"),
    path("locked/", locked_view, name="locked"),
]
