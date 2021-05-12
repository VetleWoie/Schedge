from django.shortcuts import render, redirect
import django
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
import datetime as dt
from .forms import EventForm, TimeSlotForm, InviteForm, FriendForm, NameForm
from .models import Event, TimeSlot, Invite, PotentialTimeSlot, FriendRequest
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.timezone import get_current_timezone
from collections import namedtuple
import re

from .model_utils import riise_hofsøy, create_time_slot
from .utils import time_diff

from django.db.models.signals import post_save
from notifications.signals import notify
from notifications.models import Notification


def home(request):
    user_count = User.objects.count()
    context = {"user_count": user_count}
    if request.user.is_authenticated:
        return redirect(mypage)

    return render(request, "home.html", context)


@login_required(login_url="/login/")
def mypage(request):
    user = request.user
    host_undecided = Event.objects.filter(host=user, status="U")
    host_decided = Event.objects.filter(host=user, status="C")

    participant_as_guest = Event.objects.filter(participants=user).exclude(host=user)

    invites = Invite.objects.filter(invitee=user)

    friends = request.user.profile.friends.all()

    # Get events that will happen in between today and within the next seven days
    today = dt.date.today()
    in_seven_days = today + dt.timedelta(days=7)
    this_weeks_events = Event.objects.filter(participants=user, status="C", startdate__gte=today, enddate__lte=in_seven_days)

    context = {
        "host_undecided": host_undecided,
        "host_decided": host_decided,
        "participant_as_guest": participant_as_guest,
        "invites": invites,
        "this_week": this_weeks_events,
        "friends": friends
    }
    return render(request, "mypage.html", context)


# from .models import User
# Create your views here.
@login_required(login_url="/login/")
def create_event(request):
    """Creates an event.

    Uses the 'request' argument passed to create a new event.

    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request,
        which HTTP method, potential files.

    Returns
    -------
        Return a HttpResponse whose content is filled with the result
        of calling django.template.loader.render_to_string() with 'context'
        or return an HttpResponseRedirect to the event.
    """
    if request.method == "POST":
        # pressed submit
        host = request.user
        # get info in the form
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            # create new event with stuff in form
            # because EventForm is model of Event, we can safely use kwarg
            newevent = Event.objects.create(**data, host=host)
            newevent.participants.add(host)
            return redirect(event, newevent.id)
        else:
            return render(request, "createevent.html", {"form": form}, status=400)

    # GET
    form = EventForm()  # empty form
    context = {"form": form}
    return render(request, "createevent.html", context)


@login_required(login_url="/login/")
def event(request, event_id):
    """Gets an event or creats a timeslot.

    Uses the 'request' argument to return an event or create a
    new timeslot.

    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request
        and which HTTP method.
    event_id : int
        Id of the event that the request is trying to reach
    Returns
    -------
        Return a HttpResponse whose content is filled with the result
        of calling django.template.loader.render_to_string() with 'context'
        or return an HttpResponseRedirect to the event.
    """
    try:
        # select * from Event where id=event_id;
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404("404: not valid event id")

    if request.method == "POST":
        timeslotform = TimeSlotForm(request.POST, duration=this_event.duration)
        creator = request.user
        if timeslotform.is_valid() and creator.is_authenticated:
            timeslotdata = timeslotform.cleaned_data
            create_time_slot(this_event, creator, timeslotdata)

        else:
            # TODO: rewrite maybe.
            # shouldn't be possible through the website though. only through manual post
            return HttpResponseBadRequest("Invalid Form!")


    participating = this_event.participants.filter(id=request.user.id).exists()
    if not participating:
        return HttpResponse('Unauthorized', status=401)
    potentialtimeslots = PotentialTimeSlot.objects.filter(event=this_event)
    timeslots = TimeSlot.objects.filter(event=this_event)
    # new time slot form with this event's start date and end date
    timeslotform = TimeSlotForm()
    timeslotform.set_limits(this_event)

    participants = this_event.participants.all()
    invites = Invite.objects.filter(event=this_event)

    inviteform = InviteForm(invites=invites, accepted=participants, user=request.user)
    
    friends = request.user.profile.friends

    context = {
        "event": this_event,
        "timeslotform": timeslotform,
        "timeslots": timeslots,
        "inviteform": inviteform,
        "participants": participants,
        "invites": invites,
        "pts": potentialtimeslots,
        "friends": friends,
    }
    return render(request, "event.html", context)


@login_required(login_url="/login/")
def timeslot_delete(request, event_id, timeslot_id):
    """Deletes a timeslot and reevaluates the timeslots.

    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request
        and which HTTP method.
    event_id : int
        Id of the event that the request is trying to reach
    timeslot_id : int
        Id of the timeslot in the event that will be deleted
    Returns
    -------
        A HttpResonse that redirects to the event.
    """
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
        riise_hofsøy(this_event)

    return redirect(event, event_id)


def timeslot_select(request, event_id):
    """ Selects the final timeslot.

    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request
        and which HTTP method.
    event_id : int
        Id of the event that the request is trying to reach

    Returns
    -------
        A HttpResonse that redirects back to the event.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Request method not allowed")

    try:
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404("Not valid event id")

    time = request.POST["options"]
    start, end, date = time.split(",")

    def parse_timestring(time):
        """Parse the fuzzy timestamps."""
        return dt.datetime.strptime(time, '%H:%M').time()
    def parse_datestring(time):
        """Parse the fuzzy timestamps."""
        return dt.datetime.strptime(time, '%Y-%m-%d').date()

    start = parse_timestring(start)
    end = parse_timestring(end)
    date = parse_datestring(date)

    if time_diff(start, end) != this_event.duration:
        return HttpResponseBadRequest("the selected time does not have the same length as the duration of the event")

    this_event.status = "C"
    tz = get_current_timezone()
    this_event.chosen_time = dt.datetime.combine(date, start, tzinfo=tz)
    this_event.save()

    users = this_event.participants.exclude(id=request.user.id)
    notify.send(
        request.user,
        recipient=users,
        target=this_event,
        verb="time selected",
        title=this_event.title,
        url=f"/event/{this_event.id}/",
    )

    return redirect(event, event_id)

def notify_if_changed(event, newdata, user):
    """Sends notification from user to all participants
    if the new data is different than the event's old data.
    
    Parameters
    ----------
    event : event_object
        The event that has modified its data.
    newdata : array
        The new data that has been changed to.
    """
    if any(getattr(event, k) != newdata[k] for k in newdata):
        # there is at least one difference
        # send notifications to all attendees except ourselves.
        users = event.participants.exclude(id=user.id)

        # send notifications
        notify.send(
            user,
            recipient=users,
            target=event,
            verb="event edited",
            title=event.title,
            url=f"/event/{event.id}/",
        )



@login_required(login_url="/login/")
def eventedit(request, event_id):
    """Edits an event
    
    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request
        and which HTTP method.
    event_id : int
        Id of the event that the request is trying to reach.
    
    Returns
    -------
        Return a HttpResponse whose content is filled with the result
        of calling django.template.loader.render_to_string() with 'context'
    """
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

            # notify only if the event was actually changed
            notify_if_changed(this_event, data, request.user)
            # update the event
            this_event.__dict__.update(data)

            # update the image seperately. use oldimg if Key Error
            this_event.image = request.FILES.get("image", oldimg)
            this_event.save()
            return redirect(event, this_event.id)
        else:
            return HttpResponseBadRequest("Invalid Form!")

    # create form with info from the current event
    seconds = this_event.duration.seconds
    initial_times = {
        "starttime": this_event.starttime.strftime("%H:%M"),
        "endtime": this_event.endtime.strftime("%H:%M"),
        # [days, hours, minutes]
        "duration": [seconds // 86400, (seconds // 3600) % 24, (seconds // 60) % 60],
    }

    form = EventForm(instance=this_event, initial=initial_times)
    context = {"event": this_event, "form": form}

    return render(request, "eventedit.html", context)


@login_required(login_url="/login/")
def event_delete(request, event_id):
    """Deletes an event and notifies the participants.
    
    Parameters
    ----------
    request : dict
        A dictionary containing the user who sent the request
        and which HTTP method.
    event_id : int
        Id of the event that the request is trying to reach.
    
    Returns
    -------
        Return a HttpResponse that redirects to mypage.
    """
    try:
        event_del = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("Event not found")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    if request.user != event_del.host:
        return HttpResponse("Unauthorized", status=401)

    timeslots = TimeSlot.objects.filter(id=event_id)
    timeslots.delete()

    Notification.objects.filter(target_object_id=event_del.id).delete()

    users = event_del.participants.exclude(id=request.user.id)
    notify.send(
        request.user,
        recipient=users,
        target=None,
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
    
    # Only the host can invite people:
    if request.user != this_event.host:
        return HttpResponse("Unauthorized", status=401)
    
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
                target=invite,
                verb="event invite",
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
        return HttpResponseNotFound("Unknown invite")

    if invite.invitee != request.user:
        return HttpResponse("Unautherized", status=401)

    try:
        notif = Notification.objects.get(target_object_id=invite.id)
    except Notification.DoesNotExist:
        pass
    else:
        notif.mark_as_read()

    invite.event.participants.add(invite.invitee)

    notify.send(
        invite.invitee,
        recipient=invite.inviter,
        target=invite,
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
        return HttpResponseNotFound("Unknown invite")

    if invite.invitee != request.user:
        return HttpResponse("Unautherized", status=401)

    try:
        notif = Notification.objects.get(target_object_id=invite.id)
    except Notification.DoesNotExist:
        pass
    else:
        notif.mark_as_read()

    # send invite to inviter that the invite was rejected
    notify.send(
        invite.invitee,
        recipient=invite.inviter,
        target=None,
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
        return HttpResponseNotFound("Unknown invite")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    if invite.event.host != request.user:
        return HttpResponse("Unauthorized", status=401)

    #  silently remove the notifications
    try:
        notification = Notification.objects.get(target_object_id=invite.id)
    except Notification.DoesNotExist:
        pass
    else:
        notification.delete()

    invite.delete()
    return redirect(event, invite.event.id)


def participant_delete(request, event_id, user_id):
    try:
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("Unknown event")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    try:
        user = this_event.participants.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseNotFound("Unknown User")

    if this_event.host != request.user or this_event.host == user:
        return HttpResponse("Unauthorized", status=401)

    # remove the timeslots created by this user
    TimeSlot.objects.filter(event=this_event, creator=user).delete()
    # remove user from the event's participants
    this_event.participants.remove(user)

    # send notification to deleted user
    notify.send(
        request.user,
        recipient=user,
        target=this_event,
        verb=f"participant deleted",
        title=this_event.title,
        url=f"/mypage/",
    )

    return redirect(event, this_event.id)


def participant_leave(request, event_id, user_id):
    try:
        this_event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound("Unknown event")

    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")

    try:
        user = this_event.participants.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseNotFound("Unknown User")

    # remove the timeslots created by this user
    TimeSlot.objects.filter(event=this_event, creator=user).delete()
    # remove user from the event's participants
    this_event.participants.remove(user)

    # notify host that user left
    notify.send(
        user,
        recipient=this_event.host,
        target=this_event,
        verb=f"participant left",
        title=this_event.title,
        url=f"/event/{this_event.id}",
    )
    return redirect(mypage)


def mark_notification_as_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id)
    except Notification.DoesNotExist:
        return HttpResponseNotFound("notification not found", status=404)
    notif.mark_as_read()
    return HttpResponse("ok", status=200)


def termsandservices(request):
    return render(request, "termsandservices.html")

@login_required
def delete_user(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Bad request")
    
    user = request.user
    user.delete()        
    return redirect(home)

@login_required(login_url="/login/")
def friend_request_send(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad Request')
    if not request.POST.get("to_user", False): 
        return HttpResponseBadRequest("The form is empty")
    form = FriendForm(request.POST)
    if form.is_valid():
        from_user = request.user
        to_user = User.objects.get(username=request.POST['to_user'])
        if to_user == from_user:
            return HttpResponseBadRequest('You cannot add yourself as a friend')
        if from_user.profile.friends.filter(id=to_user.id).exists():
            return HttpResponseBadRequest("You are already friends with this user")
        friend_req, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        if created:
            notify.send(
                request.user,
                recipient=to_user,
                verb="friend request",
                request_id=friend_req.id,
                url=f"",
            )
            return HttpResponse('Friend request sent successfully')
        else:
            return HttpResponse('Friend request was already sent')
    else:
        return HttpResponseNotFound('user not found')

@login_required(login_url='/login/')
def friend_request_delete(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad request') 
    form = FriendForm(request.POST)
    if form.is_valid() and FriendRequest.objects.filter(from_user=request.user, to_user=User.objects.get(username=form.cleaned_data['to_user'])).exists():
        friend_req = FriendRequest.objects.get(from_user=request.user, to_user=User.objects.get(username=form.cleaned_data['to_user']))
        friend_req.delete()
        return HttpResponse('Request deleted')
    else:
        return HttpResponseNotFound('Not found')

@login_required(login_url='/login/')
def friend_request_accept(request, request_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad Request')
    if not FriendRequest.objects.filter(id=request_id).exists():
        return HttpResponseNotFound('Not found')

    friend_req = FriendRequest.objects.get(id=request_id)
    if not friend_req.to_user == request.user:
        return HttpResponseBadRequest('Error')

    to_user = User.objects.get(username=friend_req.to_user)
    from_user = User.objects.get(username=friend_req.from_user)
    from_user.profile.friends.add(to_user)
    to_user.profile.friends.add(from_user)
    
    notify.send(
        request.user,
        recipient=friend_req.from_user,
        verb="friend request accepted",
        url=f"", #TODO fix url?
    )
    
    friend_req.delete()

    return HttpResponse('Friend request accepted')

@login_required(login_url='/login/')
def friend_request_reject(request, request_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad Request')
    if not FriendRequest.objects.filter(id=request_id).exists():
        return HttpResponseNotFound('Bad Request')
    
    friend_request = FriendRequest.objects.get(id=request_id)
    if not friend_request.to_user == request.user:
        return HttpResponseBadRequest('Error')
    friend_request.delete()
    return HttpResponse('Friend request rejected')

@login_required(login_url='/login/')
def friend_delete(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Bad request')
    form = FriendForm(request.POST)
    if form.is_valid() and request.user.profile.friends.filter(username=form.cleaned_data['to_user']).exists():
        friend = request.user.profile.friends.get(username=form.cleaned_data['to_user'])
        request.user.profile.friends.remove(friend)
        friend.profile.friends.remove(request.user)
        return HttpResponse('friend removed')
        
    return HttpResponseNotFound('Bad request')