from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inicio(request):
    return render(request, 'core/dashboard.html', {'section': 'dashboard'})
