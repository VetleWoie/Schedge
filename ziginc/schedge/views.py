from django.shortcuts import render, redirect
import django
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
import datetime as dt
from .forms import EventForm, TimeSlotForm, InviteForm
from .models import Event, TimeSlot, Participant, Invite
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import NameForm
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User


@login_required(login_url="/login/")
def mypage(request):
    user = request.user
    hostUndecided = Event.objects.filter(host=user, status="U")
    hostDecided = Event.objects.filter(host=user, status="C")
    upcomingParticipant = Participant.objects.filter(user=user, ishost=False)
    invites = Invite.objects.filter(invitee=user)
    # upcomingParticipant = userevents.exclude(hostID=Simulated_user)
    context = {
        "hostUndecided": hostUndecided,
        "upcomingHost": hostDecided,
        "upcomingParticipant": upcomingParticipant,
        "invites": invites,
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
                return render(request, "createevent.html", {"form": form}, status=400)
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
        raise Http404("404: not valid event id")

    if request.method == "POST":
        timeslotform = TimeSlotForm(request.POST)
        creator = request.user

        if timeslotform.is_valid()  and creator.is_authenticated:
            timeslotdata = timeslotform.cleaned_data
            newtimeslot = TimeSlot.objects.create(
                event=this_event, creator=creator, **timeslotdata
            )
        else:
            # TODO: rewrite maybe.
            # shouldn't be possible through the website though. only through manual post
            return HttpResponseBadRequest("Invalid Form!")

    # only timeslots from this event
    timeslots = TimeSlot.objects.filter(event=this_event)

    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)

    inviteform = InviteForm(user=request.user)
    # print(inviteform)

    context = {
        "event": this_event,
        "timeslotform": timeslotform,
        "timeslots": timeslots,
        "inviteform": inviteform,
    }
    return render(request, "event.html", context)


@login_required(login_url="/login/")
def timeslot_delete(request, event_id, timeslot_id):
    if request.method == "POST":
        try:
            # select * from Event where id=event_id;
            this_event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Http404("Not valid event id")

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

    # create form with info from the current event¨
    seconds = this_event.duration.seconds
    initial_times = {
        "starttime": this_event.starttime.strftime("%H:%M"),
        "endtime": this_event.endtime.strftime("%H:%M"),
        "duration": [seconds // 86400, (seconds // 3600) % 24, (seconds // 60) % 60],
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

    return redirect(mypage)


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
            userData = form.cleaned_data
            userData.pop("password2")  # Remove retype password from dict

            user = User.objects.create_user(**userData)  # Create User from dict
            login(request, user)  # Log user in
            return redirect(reverse("mypage"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def event_invite(request, event_id):
    try:
        # select * from Event where id=event_id;
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("404: not valid event id")
    if request.method != "POST":
        return HttpResponseBadRequest(
            "invite view does not support other than post method"
        )
    form = InviteForm(request.POST, user=request.user)
    if form.is_valid():
        data = form.cleaned_data
        invitee = data["invitee"]
        invirer = request.user
        is_duplicate = Invite.objects.filter(
            event=this_event, inviter=invirer, invitee=invitee
        ).exists()

        if is_duplicate:
            # TODO: what do we do?
            return HttpResponseBadRequest("You have already invited this person!")
            pass
        elif invitee == request.user:
            return HttpResponseBadRequest("You cannot invite yourself")
        else:
            invite = Invite.objects.create(
                event=this_event,
                inviter=invirer,
                invitee=invitee,
                senttime=django.utils.timezone.now(),
            )
    else:
        return HttpResponseBadRequest("Invalid Form!")
    return redirect(event, event_id)


def invite_accept(request, invite_id):
    return HttpResponseBadRequest(":)")


def invite_reject(request, invite_id):
    return HttpResponseBadRequest(":(")