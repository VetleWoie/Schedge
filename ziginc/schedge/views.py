from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event

# Create your views here.

def mypage(request):
    events = Event.object.all()
    context = {'events':events}
    return render(request, 'mypage.html', context)