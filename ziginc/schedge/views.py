from django import template
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .form import NameForm
from .admin import createUser

# from .models import User
# Create your views here.

def createEvent(request):
    raise Http404("THIS DOES NOT Existss") #tis' was but a test

def SignUpView(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        print('yoooo is this valid?')
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:'
            createUser(request)
            return HttpResponseRedirect('login')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'registration/signup.html', {'form': form})