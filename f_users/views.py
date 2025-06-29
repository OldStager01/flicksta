from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Profile
from .forms import ProfileForm
from f_posts.forms import ReplyCreateForm
from django.http import Http404
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.utils import send_email_confirmation
# Create your views here.
def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(Profile, user__username=username)
        if request.htmx:
            print("HTMX request detected")
            if 'top-posts' in request.GET:
                posts = profile.user.posts.annotate(like_count=Count('likes')).filter(like_count__gt=0).order_by('-like_count')
            elif 'top-comments' in request.GET:
                comments = profile.user.comments.annotate(like_count=Count('likes')).filter(like_count__gt=0).order_by('-like_count')
                replyform = ReplyCreateForm()
                return render(request, 'f_users/snippets/loop_profile_comments.html', {'comments': comments, 'replyform': replyform})
            elif 'liked-posts' in request.GET:
                posts = profile.user.likedposts.all()
            else:
                posts = profile.user.posts.all()
            return render(request, 'f_users/snippets/loop_profile_posts.html', {'posts': posts})
    else:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist")

    posts = profile.user.posts.all()
    return render(request, 'f_users/profile.html', {'profile': profile, 'posts': posts})

@login_required
def profile_edit_view(request):
    print("Path", request.path)
    form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            print("VERIFIED", request.user.emailaddress_set.get(primary=True).verified)
            if request.user.emailaddress_set.get(primary=True).verified:
                return redirect('profile-view')
            else:
                return redirect('profile-verify-email')
    return render(request, 'f_users/profile-edit.html', {'form': form})

@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == 'POST':
        try:
            logout(request)
            user.delete()
            messages.success(request, "Your profile has been deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting your profile: {e}")
        finally:
            return redirect('home')  # Redirect to a suitable page after deletion
    return render(request, 'f_users/profile-delete.html')

@login_required
def profile_verify_email_view(request):
    send_email_confirmation(request, request.user)
    return redirect('profile-view')