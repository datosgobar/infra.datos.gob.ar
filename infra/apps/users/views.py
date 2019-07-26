from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

# Create your views here.
from django.urls import reverse


@login_required
def home(request):
    """View function for home page of site."""

    return HttpResponseRedirect(reverse('catalog:nodes'))
