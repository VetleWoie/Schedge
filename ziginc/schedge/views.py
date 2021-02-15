from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event
import datetime #Only used to get som eevents into the dummy database. Remove before deployment.

# Create your views here.
Simulated_user = 1
def mypage(request):
    hostUndecided = Event.objects.filter(hostID=Simulated_user, status='U')
    hostDecided = Event.objects.filter(hostID=Simulated_user, status='C')
    upcomingParticipant = Event.objects.filter(status='C').exclude(hostID=Simulated_user)
    context = {'hostUndecided':hostUndecided,
                'upcomingHost':hostDecided,
                'upcomingParticipant':upcomingParticipant}
    return render(request, 'mypage.html', context)