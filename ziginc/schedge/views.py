from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest

from .forms import EventForm, TimeSlotForm
from .models import Event, TimeSlot

# Create your views here.

def create_event(request):
    if request.method == 'POST':
        # pressed submit

        # get info in the form
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            data = form.cleaned_data
            # create new event with stuff in form
            # because EventForm is model of Event, we can safely use kwargs
            print(data)
            newevent = Event.objects.create(**data)
            return redirect(event, newevent.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    # GET
    form = EventForm()  # empty form
    context = {'form': form}
    return render(request, 'createevent.html', context)

def event(request, event_id):
    try:
        # select * from Event where id=event_id;
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("404: not valid event id")

    if request.method == "POST":
        timeslotform = TimeSlotForm(request.POST)

        if timeslotform.is_valid():    
            timeslotdata = timeslotform.cleaned_data
            newtimeslot = TimeSlot.objects.create(event=this_event, **timeslotdata)

    timeslots = TimeSlot.objects.filter(event=this_event)
    timeslotform = TimeSlotForm()

    context = {
        'event': this_event, 
        'form': timeslotform, 
        'timeslots': timeslots
    }
    return render(request, 'event.html', context)

def del_timeslot(request, event_id, timeslot_id):
    print("HERRR!!!")
    if request.method == "DELETE":
        print("Enn her??!!!")

        try:
            # select * from Event where id=event_id;
            this_event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return HttpResponseNotFound("404: not valid event id")

        try:
            timeslot = TimeSlot.objects.get(id=timeslot_id, event=event)
        except TimeSlot.DoesNotExist:
            return HttpResponseNotFound("404: not valid timeslot id")
        timeslot.delete()

    return redirect(event, event_id)
