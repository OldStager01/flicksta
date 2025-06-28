from django.contrib import admin
from django.urls import path
from .views import profile_view, profile_edit_view, profile_delete_view
urlpatterns = [
    path("", profile_view, name="profile-view"),
    path("edit/", profile_edit_view, name="profile-edit"),
    path("delete/", profile_delete_view, name="profile-delete"),
    path("onboarding/", profile_edit_view, name="user-onboarding"),
    path("<username>/", profile_view, name="user-profile"),
]
