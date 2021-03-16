from django.shortcuts import render, redirect
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
import datetime as dt
from .forms import EventForm, TimeSlotForm
from .models import Event, TimeSlot, Participant, PotentialTimeSlot
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

def find_potential_time_slots(event):
    riise_hofsøy(event)

def riise_hofsøy(event):
    def get_key(k):
        return k[0]
    def find_min(S):
        if not S:
            return None
        m = dt.datetime.combine(S[0].date,S[0].end_time)
        for ts in S:
            m = min(m, dt.datetime.combine(ts.date, ts.end_time))
        return m
    def find_max(S):
        if not S:
            return None
        mx = dt.datetime.combine(S[0].date, S[0].start_time)
        for ts in S:
            mx = max(mx, dt.datetime.combine(ts.date, ts.start_time))
        return mx
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
    cnt = 0
    min_cnt = 2 # TODO replace with event.min_cnt or equivalent
    start = dt.datetime(1,1,1,0,0,0)
    end = dt.datetime(1,1,1,0,0,0)
    for i, t in enumerate(t_table):
        cnt += t[1]
        if t[1] == +1: # step up
            S.append(t[2])
            start = t[0]
            if dt.datetime.combine(t[2].date,t[2].end_time) - t_table[i + 1][0] >= event.duration:
                end = t_table[i + 1][0]
            else:
                end = find_min(S)
        else: # step down
            if i + 1 >= len(t_table): # all tuples have been iterated
                return
            
            S.remove(t[2])
            if end - start < event.duration: # Last pts was of valid length
                start = find_max(S)
            else:
                start = dt.datetime.combine(t[2].date,t[2].end_time)
            end = t_table[i + 1][0]

        if cnt >= min_cnt and end - start >= event.duration: # Only add/update pts if new one is valid
            pts = PotentialTimeSlot.objects.filter(event=event, start_time=find_time(start), end_time=find_time(end), date=t[2].date)
            if pts.exists():
                pts[0].participants.add(t[2].creator)
            else:
                pts = PotentialTimeSlot.objects.create(event=event, start_time=find_time(start), end_time=find_time(end), date=t[2].date)
                for ts in S:
                    pts.participants.add(ts.creator)
        




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
        refactor_potential_time_slots(event)
        return
    return first
    
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
            if check_overlap_ts(this_event, creator, timeslotdata["start_time"], timeslotdata["end_time"], timeslotdata["date"], 1):
                newtimeslot = TimeSlot.objects.create(event=this_event, creator=creator, **timeslotdata)
                find_potential_time_slots(this_event) # check for new potential ts with new ts


    potentialtimeslots = PotentialTimeSlot.objects.filter(event=this_event)
    # if not potentialtimeslots:
    timeslots = TimeSlot.objects.filter(event=this_event)
    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)

    context = {"event": this_event, "form": timeslotform, "ptimeslots": potentialtimeslots, "timeslots": timeslots}
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
            userData = form.cleaned_data
            userData.pop("password2") # Remove retype password from dict

            user = User.objects.create_user(**userData) # Create User from dict
            login(request, user) # Log user in
            return redirect(reverse("mypage"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "registration/signup.html", {"form": form})
