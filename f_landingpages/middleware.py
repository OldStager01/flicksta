from .models import LandingPage
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect

def landingpage_middleware(get_response):
    def middleware(request):
    
        if page_is_enabled('Maintenance'):
            if request.path != reverse('maintenance'):
                if '/theboss/' not in request.path:
                    if settings.STAGING != True:
                        return redirect('maintenance')
                    
        if page_is_enabled('Staging'):
            if request.path != reverse('locked'):
                if '/theboss/' not in request.path:
                    if settings.STAGING == True:
                        if 'staging_access' not in request.session :
                            return redirect('locked')
                     
        response = get_response(request)
        return response

    return middleware


def page_is_enabled(page_name):
    page = LandingPage.objects.filter(name=page_name).first()
    print(page.name, page.is_enabled)
    if page:
        return page.is_enabled
    return False
    