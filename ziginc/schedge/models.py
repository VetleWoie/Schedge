from django.db import models

import datetime as dt
import django

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Create your models here.




class Event(models.Model):
    """The event model
    TODO: Add more stuff"""

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

    error_css_class = "error"

    @property
    def n_attendees(self):
        """returns the number of users who have accepted this event
        we use a property so that it can be used in templates"""
        return self.participants.count()

    def __str__(self):
        return f"Event(id={self.id}, title={self.title}, ...)"

    def clean(self):
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
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["event", "start_time", "end_time", "date", "creator"]

    def clean(self):
        if self.date < dt.date.today():
            raise ValidationError({"date": ["Cannot create event in the past"]})

    def __str__(self):
        return f"TimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}"


class PotentialTimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    participants = models.ManyToManyField(get_user_model())
    chosen = models.BooleanField(default=False)

    def __str__(self):
        return f"PotentialTimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}, participants={self.participants}"

    @property
    def split(self):
        """returns a list of the possible times within this potential time slot
        which have the same duration as the event. the times are 15 min appart, and always
        start at either 00, 15, 30 or 45.
        F.ex: pts between 11:50am and 1pm, duration is 30 min
        return [12:00 - 12:30, 12:15 - 12:45, 12:30 - 13:00]"""

        def time_add(time, delta):
            """adds a timedelta to a time object"""
            return (dt.datetime.combine(dt.date.today(), time) + delta).time()

        interval = 15
        startmin = self.start_time.minute
        duration = self.event.duration
        # round up to next quarter of an hour
        start = time_add(self.start_time, dt.timedelta(minutes=(startmin + interval - 1) & (-interval)))
        # start = self.start_time + dt.timedelta(minutes=interval - startmin % interval)
        interval_mins = dt.timedelta(minutes=interval)

        times = []
        current = start
        end = time_add(current, duration)
        print(end, self.end_time)
        while end <= self.end_time:
            times.append((current, end))

            current = time_add(current, interval_mins)
            end = time_add(current, duration)
        print(times)
        return times

class Invite(models.Model):
    inviter = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="inviter"
    )
    invitee = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="invitee"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    senttime = models.DateTimeField()

    def __str__(self):
        return f"Invite(inviter={self.inviter}, invitee={self.invitee}, event={self.event}, sent={self.senttime})"
