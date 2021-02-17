import datetime as dt

from django.shortcuts import render, redirect
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)

from .forms import EventForm, TimeSlotForm
from .models import Event, TimeSlot

# Create your views here.


def create_event(request):
    if request.method == "POST":
        # pressed submit

        # get info in the form
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            # create new event with stuff in form
            # because EventForm is model of Event, we can safely use kwargs
            newevent = Event.objects.create(**data)
            return redirect(event, newevent.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    # GET
    form = EventForm()  # empty form
    context = {"form": form}
    return render(request, "createevent.html", context)


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

    # only timeslots from this event
    timeslots = TimeSlot.objects.filter(event=this_event)

    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)

    context = {"event": this_event, "form": timeslotform, "timeslots": timeslots}
    return render(request, "event.html", context)


def timeslot_delete(request, event_id, timeslot_id):
    if request.method == "POST":
        try:
            # select * from Event where id=event_id;
            this_event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return HttpResponseNotFound("404: not valid event id")

        try:
            timeslot = TimeSlot.objects.get(id=timeslot_id, event=this_event)
        except TimeSlot.DoesNotExist:
            return HttpResponseNotFound("404: not valid timeslot id")

        timeslot.delete()

    return redirect(event, event_id)


def eventedit(request, event_id):
    try:
        # select * from Event where id=event_id;
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("404: not valid event id")

    if request.method == "POST":
        # get info in the form
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            oldimg = this_event.image
            this_event.__dict__.update(data)
            print(request.FILES)
            print(data)
            this_event.image = request.FILES.get("image", oldimg)
            this_event.save()

            return redirect(event, this_event.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    initial_times = {
        "starttime": this_event.starttime.strftime("%H:%M"),
        "endtime": this_event.endtime.strftime("%H:%M"),
    }
    form = EventForm(instance=this_event, initial=initial_times)

    context = {"event": this_event, "form": form, "imageurl": this_event.image.url}
    return render(request, "eventedit.html", context)


def event_delete(request, event_id):

    # try:
    if request.method == "POST":
        Event.objects.get(id=event_id).delete()
        timeslots = TimeSlot.objects.filter(id=event_id)
        timeslots.delete()

    return redirect(event, event_id)
    # return redirect(mypage)
