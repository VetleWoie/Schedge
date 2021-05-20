from django.db import models

import datetime as dt
import django

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from .utils import time_add, time_diff

class Profile(models.Model):
    """A class to represent an extended one-to-one
    django user model.

    Attributes
    ----------
    user : Django user object
        The user related to this instance of the class.
    friends : Django user objects
        Relates this user to another user.
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    friends = models.ManyToManyField(get_user_model(), related_name='friend', blank=True)

    def __str__(self):
        return f"{self.user}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Links the 'Profile' model to the Django user model on creation"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the 'Profile' model whenever the Django user model is saved"""
    instance.profile.save()
    
class FriendRequest(models.Model):
    """A class to represent a friend request model
    
    Attributes
    ----------
    from_user : Django user object
        The user who sent the friend request
    to_user : Django user object
        The user who receives the friend request
    """
    from_user = models.ForeignKey(
        User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        User, related_name='to_user', on_delete=models.CASCADE)

    def __str__(self):
        return f"FriendRequest(id={self.id}, from={self.from_user}, to={self.to_user})"
    
class Event(models.Model):
    """A class to represent event model
    
    Attributes
    ----------
    title : string
        The title of the event
    location : string
        The location of the event
    description : string
        Description of the event (may be blank)
    starttime : time
        Earliest time of the day the event may start
    endtime : time
        Latest time of the day the event may end
    startdate : time
        Earliest date the event may occur
    enddate : time
        Latest date the event may occur
    duration : timedelta
        Minimum duration of the event (may be zero)
    image : image file
        Header image of the event
    status : string
        Describes the state of the event (default is Unresolved).
        (See STATUS_OPTIONS for more options)
    STATUS_OPTIONS : tuple
        Unresolved : A time and date has not yet been decided for the event
        Chosen : The time and date has been decided for the event
        Finishied : The event is over
    host : Django user object
        The user who created the event, works as a moderator
    participants : Django user object
        Other users who are to participate to the event
    chosen_time : date time
        The date and time when the event will be held (default as blank)
    error_css_class : string

    """

    STATUS_OPTIONS = (("C", "Chosen"), ("U", "Unresolved"), ("F", "Finished"))
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True, max_length=5000)

    starttime = models.TimeField(default=django.utils.timezone.now)
    endtime = models.TimeField(default=django.utils.timezone.now)

    startdate = models.DateField(default=django.utils.timezone.now)
    enddate = models.DateField(default=django.utils.timezone.now)

    duration = models.DurationField(
        max_length=dt.timedelta(hours=10), default=dt.timedelta()
    )

    image = models.ImageField(default="default.jpg", upload_to="images/")
    status = models.CharField(max_length=10, default="U", choices=STATUS_OPTIONS)
    host = models.ForeignKey(
        get_user_model(), default=1, on_delete=models.CASCADE, related_name="host"
    )
    participants = models.ManyToManyField(get_user_model(), related_name="participants")

    chosen_time = models.DateTimeField(null=True)

    error_css_class = "error"

    @property
    def n_attendees(self):
        """returns the number of users who have accepted this event
        we use a property so that it can be used in templates"""
        return self.participants.count()

    def __str__(self):
        return f"Event(id={self.id}, title={self.title}, ...)"

    def clean(self):
        """Validates the start and end times before creating the model"""
        earliest = dt.datetime.combine(self.startdate, self.starttime)
        latest = dt.datetime.combine(self.enddate, self.endtime)

        if self.startdate < dt.date.today():
            raise ValidationError({"startdate": ["Cannot create event in the past"]})

        if earliest > latest:
            raise ValidationError(
                {
                    "startdate": [
                        "Your earliest possible time is after the latest possible"
                    ],
                    "enddate": [
                        "Your earliest possible time is after the latest possible"
                    ],
                }
            )

        if (latest - earliest) < self.duration:
            raise ValidationError(
                {"duration": ["The allotted time is shorter than the duration"]}
            )

        if self.duration < dt.timedelta(0):
            raise ValidationError(
                {
                    "duration": [
                        "Negative duration! Time's arrow neither stands still nor reverses. It merely marches forward."
                    ]
                }
            )


class TimeSlot(models.Model):
    """A class that represents the time slot model
    used to suggest a time and date for the event to take place

    Attributes
    ----------
    event : event model object
        The event this time slot is related to
    start_time : time
        The suggested time slot start time
    end_time : time
        The suggested time slot end time
    date : date
        Date of the suggested time
    creator : Django user object
        User whom suggested this time slot
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["event", "start_time", "end_time", "date", "creator"]

    def clean(self):
        """Validates the 'date' field"""
        if self.date < dt.date.today():
            raise ValidationError({"date": ["Cannot create event in the past"]})

    def __str__(self):
        return f"TimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}"


class PotentialTimeSlot(models.Model):
    """A class that represents the potential time slot model

    A potential time slot is a time slot the event can take place
    because multiple users are available in this interval

    Attributes
    ----------
    event : event model object
        The event this time slot is related to
    start_time : time
        The suggested time slot start time
    end_time : time
        The suggested time slot end time
    date : date
        Date of the suggested time
    participants : Django user objects
        The users whom may attend the event in this time slot
    chosen : Boolean
        True indicates that the event will take place during
        this time slot
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    participants = models.ManyToManyField(get_user_model())
    chosen = models.BooleanField(default=False)

    def __str__(self):
        return f"PotentialTimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}, participants={self.participants}"

    @property
    def n_participants(self):
        """Returns the amount of participants available in this time slot"""
        return self.participants.count()

    @property
    def split(self):
        """Returns a list of the possible times within this potential time slot
        which have the same duration as the event. the times are 15 min appart, and always
        start at either 00, 15, 30 or 45.
        F.ex: pts between 11:50am and 1pm, duration is 30 min
        return [12:00 - 12:30, 12:15 - 12:45, 12:30 - 13:00]"""
 
        interval = 15
        startmin = self.start_time.minute
        duration = self.event.duration
        # round up to next quarter of an hour
        start = time_add(self.start_time, dt.timedelta(minutes=(startmin + interval - 1) // interval * interval))
        # start = self.start_time + dt.timedelta(minutes=interval - startmin % interval)
        interval_mins = dt.timedelta(minutes=interval)

        times = []
        current = start
        end = time_add(current, duration)
        while end <= self.end_time:
            times.append((current, end))

            current = time_add(current, interval_mins)
            end = time_add(current, duration)
        return times

class Invite(models.Model):
    """A class that represents an event initation model
    
    Attributes
    ----------
    inviter : Django user object
        The user who sent the event invite
    invitee : Django user object
        The user who was invited
    event : event object
        Event the 'invitee' was invited to
    senttime : date time
        Date and time when the invitation was sent
    """
    inviter = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="inviter"
    )
    invitee = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="invitee"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    senttime = models.DateTimeField()

    def __str__(self):
        return f"Invite(id={self.id}, inviter={self.inviter}, invitee={self.invitee}, event={self.event}, sent={self.senttime})"
