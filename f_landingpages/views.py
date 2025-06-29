from django.shortcuts import render
from .forms import AccessForm
from .models import LandingPage
from django.shortcuts import redirect

def maintenance_view(request):
    return render(request, 'f_landingpages/maintenance.html')

def locked_view(request):
    form = AccessForm()
    if request.method == 'POST':
        form = AccessForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data.get('password')
            try:
                access_code = LandingPage.objects.filter(name='Staging').first().access_code
                if input_code == access_code:
                    request.session['staging_access'] = True
                    return redirect('home')
            except:
                pass
    return render(request, 'f_landingpages/locked.html', {'form': form})