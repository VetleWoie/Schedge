from django.shortcuts import render, redirect
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
import datetime as dt
from .forms import EventForm, TimeSlotForm
from .models import Event, TimeSlot, Participant
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import NameForm
from django.template import loader
from django.urls import reverse_lazy
from django.urls import reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .admin import createUser


# Create your views here.
Simulated_user = 1


@login_required(login_url="/login/")
def mypage(request):
    hostUndecided = Event.objects.filter(host=Simulated_user, status="U")
    hostDecided = Event.objects.filter(host=Simulated_user, status="C")
    upcomingParticipant = Participant.objects.filter(user=Simulated_user, ishost=False)

    # upcomingParticipant = userevents.exclude(hostID=Simulated_user)
    context = {
        "hostUndecided": hostUndecided,
        "upcomingHost": hostDecided,
        "upcomingParticipant": upcomingParticipant,
    }
    return render(request, "mypage.html", context)


# from .models import User
# Create your views here.
@login_required(login_url="/login/")
def create_event(request):
    if request.method == "POST":
        # pressed submit
        host = request.user
        if host.is_authenticated:
            # get info in the form
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                # create new event with stuff in form
                # because EventForm is model of Event, we can safely use kwarg
                newevent = Event.objects.create(**data, host=host)
                newparticipant = Participant.objects.create(
                    event=newevent, user=host, ishost=True
                )
                return redirect(event, newevent.id)
            else:
                return HttpResponseBadRequest("Invalid Form!")
        else:
            return HttpResponseBadRequest("Sign in to create an event!")

    # GET
    form = EventForm()  # empty form
    context = {"form": form}
    return render(request, "createevent.html", context)


@login_required(login_url="/login/")
def event(request, event_id):
    try:
        # select * from Event where id=event_id;
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("404: not valid event id")

    if request.method == "POST":
        timeslotform = TimeSlotForm(request.POST)
        creator = request.user

        if timeslotform.is_valid() and creator.is_authenticated:
            timeslotdata = timeslotform.cleaned_data
            newtimeslot = TimeSlot.objects.create(
                event=this_event, creator=creator, **timeslotdata
            )

    # only timeslots from this event
    timeslots = TimeSlot.objects.filter(event=this_event)

    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)

    context = {"event": this_event, "form": timeslotform, "timeslots": timeslots}
    return render(request, "event.html", context)

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
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

            this_event.image = request.FILES.get("image", oldimg)
            this_event.save()

            return redirect(event, this_event.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    # create form with info from the current event
    initial_times = {
        "starttime": this_event.starttime.strftime("%H:%M"),
        "endtime": this_event.endtime.strftime("%H:%M"),
    }
    form = EventForm(instance=this_event, initial=initial_times)

    context = {"event": this_event, "form": form}
    return render(request, "eventedit.html", context)

@login_required(login_url="/login/")
def event_delete(request, event_id):

    if request.method == "POST":
        Event.objects.get(id=event_id).delete()
        timeslots = TimeSlot.objects.filter(id=event_id)
        timeslots.delete()

    return redirect(event, event_id)
    # return redirect(mypage)


def signUpView(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:'
            createUser(request)
            return redirect(mypage)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "registration/signup.html", {"form": form})
