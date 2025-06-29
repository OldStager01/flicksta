from django.test import TestCase
from django.urls import reverse
from f_posts.models import Post
from django.contrib.auth.models import User

class BaseSetup(TestCase):
    def setUp(self):
        user_data = {
            "email":"test@gmail.com",
            "username":"testuser",
            "password1":"testpassword123",
            "password2":"testpassword123"
        }
        self.client.post(reverse("account_signup"), user_data, format="text/html")

class PostCreateTest(BaseSetup):
    def test_post_create(self):
        response = self.client.get(reverse("post-create"))
        self.assertEqual(response.status_code, 200)
        
        form_data = {
            "url" : "https://example.com",
            "body" : "This is a test post",
        }
         
         
        self.user = User.objects.get(username="testuser")
        post_data = {
            'url': form_data['url'],
            'body': form_data['body'],
            'title': 'Test Post',
            'image': 'https://picsum.photos/200/300',
            'artist': 'Test Artist',
            'author': self.user          
        }
        
        post = Post.objects.create(**post_data)
        self.assertEqual(Post.objects.filter(title=post.title).exists(), True )
        
        homepage = self.client.get(reverse("home"))
        self.assertContains(homepage, post.title)
        
        post.delete()
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, post.title)
        