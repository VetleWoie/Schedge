from django.shortcuts import render, redirect
import django
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
import datetime as dt
from .forms import EventForm, TimeSlotForm, InviteForm
from .models import Event, TimeSlot, Participant, Invite, PotentialTimeSlot
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

def find_potential_time_slots(event):
    riise_hofsøy(event)

def riise_hofsøy(event):
    def get_key(k):
        return k[0]
    def find_time(t):
        return dt.datetime.strptime(dt.datetime.strftime(t, '%H:%M'), "%H:%M").time()        
        
    time_slots = TimeSlot.objects.filter(event=event)
    PotentialTimeSlot.objects.filter(event=event).delete()

    t_table = []
    for ts in time_slots:
        t_table.append((dt.datetime.combine(ts.date, ts.start_time), +1, ts))
        t_table.append((dt.datetime.combine(ts.date, ts.end_time), -1, ts))
    t_table.sort(key=get_key)

    S = []
    in_pts = []
    cnt = 0
    min_cnt = 2 # TODO replace with event.min_cnt or equivalent
    start = dt.datetime(1,1,1,0,0,0)
    end = dt.datetime(1,1,1,0,0,0)

    for i, t in enumerate(t_table):
        cnt += t[1]
        if t[1] == 1: # step up
            S.append(t[2])
            start = t[0]
            in_pts = S.copy()

            for sub_t in t_table[i:]:
                if sub_t[1] == 1 or not sub_t[2] in in_pts:
                    continue
                end = sub_t[0]

                if len(in_pts) >= min_cnt and end - start >= event.duration: # Only add/update pts if new one is valid
                    pts = PotentialTimeSlot.objects.filter(event=event, start_time=find_time(start), end_time=find_time(end), date=t[2].date)
                    if pts.exists():
                        pts[0].participants.add(t[2].creator)
                    else:
                        pts = PotentialTimeSlot.objects.create(event=event, start_time=find_time(start), end_time=find_time(end), date=t[2].date)
                        for ts in in_pts:
                            pts.participants.add(ts.creator)
                if sub_t[2] == t[2]:
                    break
                in_pts.remove(sub_t[2])
        else: #  step down
            S.remove(t[2])




# merges new timeslot to existing from same user if they overlap
def check_overlap_ts(event, user, start, end, date, first):
    time_slots = TimeSlot.objects.filter(event=event, creator=user)
    for ts in time_slots:
        if (ts.start_time >= end or ts.end_time >= start) and date == ts.date: # Check if intersection exists
            ts_start = ts.start_time
            ts_end = ts.end_time
            ts.delete()
            return check_overlap_ts(event, user, min(start, ts_start), max(end, ts_end), date, 0)
    if not first:
        TimeSlot.objects.create(event=event, start_time=start, end_time=end, date=date, creator=user)
        riise_hofsøy(event)
        return
    return first
    
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
            if check_overlap_ts(this_event, creator, timeslotdata["start_time"], timeslotdata["end_time"], timeslotdata["date"], 1):
                newtimeslot = TimeSlot.objects.create(event=this_event, creator=creator, **timeslotdata)
                find_potential_time_slots(this_event) # check for new potential ts with new ts
            newtimeslot = TimeSlot.objects.create(
                event=this_event, creator=creator, **timeslotdata
            )
        else:
            # TODO: rewrite maybe.
            # shouldn't be possible through the website though. only through manual post
            return HttpResponseBadRequest("Invalid Form!")


    potentialtimeslots = PotentialTimeSlot.objects.filter(event=this_event)
    # if not potentialtimeslots:
    timeslots = TimeSlot.objects.filter(event=this_event)
    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)


    participants = Participant.objects.filter(event=this_event)
    invites = Invite.objects.filter(event=this_event)
    
    inviteform = InviteForm(invites=invites, accepted=participants, user=request.user)

    context = {
        "event": this_event,
        "timeslotform": timeslotform,
        "timeslots": timeslots,
        "inviteform": inviteform,
        "participants": participants,
        "invites": invites
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
        refactor_potential_time_slots(this_event)

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
    try:
        invite = Invite.objects.get(id=invite_id)
    except Invite.DoesNotExist:
        return HttpResponseBadRequest("Unknown invite")

    assert invite.invitee == request.user
    Participant.objects.create(event=invite.event, user=invite.invitee, ishost=False)

    invite.delete()

    return redirect(mypage)


def invite_reject(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id)
    except Invite.DoesNotExist:
        return HttpResponseBadRequest("Unknown invite")

    invite.delete()
    return redirect(mypage)