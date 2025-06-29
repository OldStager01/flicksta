from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User 
from f_users.models import Profile

class BaseSetup(TestCase):
    def setUp(self):
        user_data = {
            "email":"test@gmail.com",
            "username":"testuser",
            "password1":"testpassword123",
            "password2":"testpassword123"
        }
        self.client.post(reverse("account_signup"), user_data, format="text/html")


class SignUpTest(TestCase):
    def test_sign_up_page_exits(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        
    def test_sign_up_user(self):
        user_data = {
            "email":"test@gmail.com",
            "username":"testuser",
            "password1":"testpassword123",
            "password2":"testpassword123"
        }
        response = self.client.post(reverse("account_signup"), user_data, format="text/html")
        self.assertEqual(response.status_code, 302)  # Should redirect after successful signup
        
        response = self.client.get(reverse("profile-view"), args=[user_data["username"]])
        self.assertEqual(response.status_code, 200)
    
class ProfileEditTest(BaseSetup):
    def test_profile_edit(self):
        response = self.client.get(reverse("profile-edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "f_users/profile-edit.html")
        
        test_mail = "test2@gmail.com"
        form_data = {
            "email": test_mail
        }
        response = self.client.post(reverse("profile-edit"), form_data, format="text/html")
        self.assertEqual(response.status_code, 302)
        
        user_email = User.objects.get(username="testuser").email
        self.assertEqual(user_email, test_mail )
        profile_email = Profile.objects.get(user__username="testuser").email
        self.assertEqual(profile_email, test_mail)
        
        