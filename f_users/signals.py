from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Profile
from allauth.account.models import EmailAddress

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        Profile.objects.create(
            user = instance,
            email = user.email,
        )
    else:
        profile = get_object_or_404(Profile, user=user)
        profile.email = user.email
        profile.save()
        
        
@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    profile = instance
    if not created:
        user = profile.user
        if user.email != profile.email:
            user.email = profile.email
            user.save()
    
@receiver(post_save, sender=User)
def update_account_email(sender, instance, created, **kwargs):
    if not created:
        try:
            email_address = EmailAddress.objects.get(user=instance, primary=True)
            if email_address.email != instance.email:
                email_address.email = instance.email
                email_address.verified = False
                email_address.save()
        except Exception as e:
            print(f"Error updating email for user {instance.username}:", e)