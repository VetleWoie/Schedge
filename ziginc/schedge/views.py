from django import template
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
# from .models import User
# Create your views here.

def createEvent(request):
    raise Http404("THIS DOES NOT Existss") #tis' was but a test

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'