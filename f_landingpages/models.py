from django.db import models

class LandingPage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_enabled = models.BooleanField(default=True)
    access_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    