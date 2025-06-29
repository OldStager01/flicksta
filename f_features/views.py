from django.shortcuts import render
from django.conf import settings
from f_features.models import Feature
# Create your views here.
def feature_enabled(id):
    try:
        feature = Feature.objects.filter(id=id).first()    
        if (
            (settings.ENVIRONMENT == 'development' and settings.DEVELOPER == feature.developer) or
            (feature.staging_enabled and settings.STAGING == 'True') or
            (feature.production_enabled and settings.ENVIRONMENT == 'production')
        ):
            feature_enabled = True
        else:
            feature_enabled = False
        return feature_enabled
    except:
        return False   

    