from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event
import datetime #Only used to get som eevents into the dummy database. Remove before deployment.

# Create your views here.
num_dummy_events = 4

def createrandomevents():
    for i in range(num_dummy_events):
        Event.objects.create(title=f'BestEventEver{i}', 
                            duration = "14",
                            description='This is really the best event ever.',
                            location = f"YOmama{i}")
def deleterandomevents():
    for i in range(num_dummy_events):
        Event.objects.filter(title=f'BestEventEver{i}').delete()


def mypage(request):
    deleterandomevents()
    createrandomevents()
    # Event.objects.all().delete()
    events = Event.objects.all()
    context = {'events':events}
    return render(request, 'mypage.html', context)