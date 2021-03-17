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


from django.db.models.signals import post_save
from notifications.signals import notify
from notifications.models import Notification


@login_required(login_url="/login/")
def mypage(request):
    user = request.user
    host_undecided = Event.objects.filter(host=user, status="U")
    host_decided = Event.objects.filter(host=user, status="C")
    participant_as_guest = Participant.objects.filter(user=user, ishost=False)

    invites = Invite.objects.filter(invitee=user)
    # participants = userevents.exclude(hostID=Simulated_user)
    context = {
        "host_undecided": host_undecided,
        "host_decided": host_decided,
        "participant_as_guest": participant_as_guest,
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

        if timeslotform.is_valid() and creator.is_authenticated:
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

    participants = Participant.objects.filter(event=this_event)
    invites = Invite.objects.filter(event=this_event)

    inviteform = InviteForm(invites=invites, accepted=participants, user=request.user)

    context = {
        "event": this_event,
        "timeslotform": timeslotform,
        "timeslots": timeslots,
        "inviteform": inviteform,
        "participants": participants,
        "invites": invites,
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

    if request.user != this_event.host:
        return HttpResponse("Unauthorized", status=401)

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

    par = Participant.objects.filter(event=this_event, ishost=False)
    user_ids = par.values_list("user", flat=True)
    users = User.objects.filter(id__in=user_ids)

    notify.send(
        request.user,
        recipient=users,
        target=this_event,
        verb="event edited",
        title=this_event.title,
        url=f"/event/{this_event.id}/",
    )

    return render(request, "eventedit.html", context)


@login_required(login_url="/login/")
def event_delete(request, event_id):
    try:
        event_del = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("Event not found")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    if request.user != event_del.host:
        return HttpResponse("Unauthorized", status=401)

    par = Participant.objects.filter(event=event_del, ishost=False)
    user_ids = par.values_list("user", flat=True)
    users = User.objects.filter(id__in=user_ids)

    timeslots = TimeSlot.objects.filter(id=event_id)
    timeslots.delete()

    Notification.objects.filter(target_object_id=event_del.id).delete()
    notify.send(
        request.user,
        recipient=users,
        target=event_del,
        verb="event deleted",
        title=event_del.title,
        url="/mypage/",
    )

    event_del.delete()
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
        inviter = request.user
        is_duplicate = Invite.objects.filter(
            event=this_event, inviter=inviter, invitee=invitee
        ).exists()

        if is_duplicate:
            # TODO: what do we do?
            return HttpResponseBadRequest("You have already invited this person!")
        elif invitee == inviter:
            return HttpResponseBadRequest("You cannot invite yourself")
        else:
            invite = Invite.objects.create(
                event=this_event,
                inviter=inviter,
                invitee=invitee,
                senttime=django.utils.timezone.now(),
            )
            notify.send(
                inviter,
                recipient=invitee,
                target=this_event,
                verb="invite",
                title=this_event.title,
                url=f"/event/{invite.event.id}/",
                invite_id=invite.id,
            )

    else:
        return HttpResponseBadRequest("Invalid Form!")
    return redirect(event, event_id)


def invite_accept(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id)
    except Invite.DoesNotExist:
        return HttpResponseBadRequest("Unknown invite")

    try:
        notif = Notification.objects.get(target_object_id=invite.id)
    except Notification.DoesNotExist:
        pass
    else:
        notif.mark_as_read()

    assert invite.invitee == request.user
    Participant.objects.create(event=invite.event, user=invite.invitee, ishost=False)

    notify.send(
        invite.invitee,
        recipient=invite.inviter,
        target=invite.event,
        verb=f"invite accepted",
        title=invite.event.title,
        url=f"/event/{invite.event.id}/",
    )

    invite.delete()

    return redirect(mypage)


def invite_reject(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id)
    except Invite.DoesNotExist:
        return HttpResponseBadRequest("Unknown invite")

    try:
        notif = Notification.objects.get(target_object_id=invite.id)
    except Notification.DoesNotExist:
        pass
    else:
        notif.mark_as_read()

    notify.send(
        invite.invitee,
        recipient=invite.inviter,
        target=invite.event,
        verb=f"invite rejected",
        title=invite.event.title,
        url=f"/event/{invite.event.id}/",
    )
    invite.delete()
    return redirect(mypage)


def invite_delete(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id)

    except Invite.DoesNotExist:
        return HttpResponseBadRequest("Unknown invite")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    if invite.event.host != request.user:
        return HttpResponse("Unauthorized", status=401)

    invite.delete()
    return redirect(event, invite.event.id)


def participant_delete(request, participant_id):

    try:
        participant = Participant.objects.get(id=participant_id)

    except Participant.DoesNotExist:
        return HttpResponseNotFound("Unknown participant")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    if participant.event.host != request.user or participant.ishost:
        return HttpResponse("Unauthorized", status=401)

    TimeSlot.objects.filter(event=participant.event, creator=participant.user).delete()
    participant.delete()

    notify.send(
        request.user,
        recipient=participant.user,
        target=participant.event,
        verb=f"participant deleted",
        title=participant.event.title,
        url=f"/event/{participant.event.id}/",
    )

    return redirect(event, participant.event.id)


def mark_notification_as_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id)
    except Notification.DoesNotExist:
        return HttpResponseNotFound("notification not found", status=404)
    notif.mark_as_read()
    return HttpResponse("ok", status=200)
