from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event, GroupEvent
import datetime #Only used to get som eevents into the dummy database. Remove before deployment.

# Create your views here.
Simulated_user = 1
def mypage(request):
    hostUndecided = Event.objects.filter(hostID=Simulated_user, status='U')
    hostDecided = Event.objects.filter(hostID=Simulated_user, status='C')
    userevents = GroupEvent.objects.select_related('event').filter(userID=Simulated_user)
    upcomingParticipant = userevents.only("event")
    print("herrrR!!1")
    print(upcomingParticipant)
    # upcomingParticipant = userevents.exclude(hostID=Simulated_user)
    context = {'hostUndecided':hostUndecided,
                'upcomingHost':hostDecided,
                'upcomingParticipant':upcomingParticipant}
    return render(request, 'mypage.html', context)