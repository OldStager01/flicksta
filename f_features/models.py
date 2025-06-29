from django.db import models

class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    developer = models.CharField(blank=True, null=True)
    staging_enabled = models.BooleanField(default=False)
    production_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.name)
    
    class Meta: 
        ordering = ['-created_at']
    