from django.contrib import admin
from .models import Feature
# Register your models here.
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'staging_enabled', 'production_enabled')

admin.site.register(Feature, FeatureAdmin)
