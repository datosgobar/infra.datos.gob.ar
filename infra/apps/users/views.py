from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required
def home(request):
    """View function for home page of site."""

    return render(request, 'home.html')
