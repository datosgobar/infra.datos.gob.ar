from django.shortcuts import render

# Create your views here.


def home(request):
    """View function for home page of site."""

    return render(request, 'home.html')
