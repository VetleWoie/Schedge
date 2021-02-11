from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event
import datetime #Only used to get som eevents into the dummy database. Remove before deployment.

# Create your views here.
Simulated_user = 1
def mypage(request):
    hostUndecided = Event.objects.filter(hostID=Simulated_user)
    context = {'hostUndecided':hostUndecided}
    return render(request, 'mypage.html', context)