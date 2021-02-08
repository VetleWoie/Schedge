from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event
import datetime #Only used to get som eevents into the dummy database. Remove before deployment.

# Create your views here.

def mypage(request):
    events = Event.objects.all()
    context = {'events':events}
    return render(request, 'mypage.html', context)