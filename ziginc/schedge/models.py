from django.db import models

import datetime as dt
import django

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Create your models here.


class Event(models.Model):
    """The event model
    TODO: Add more stuff"""

    STATUS_OPTIONS = (("C", "Concluded"), ("U", "Unresolved"))
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
    host = models.ForeignKey(get_user_model(), default=1, on_delete=models.CASCADE)

    error_css_class = "error"

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
                {"duration": ["The allotted timespan is shorter than the duration"]}
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
    time = models.TimeField()
    date = models.DateField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["event", "time", "date"]

    def clean(self):
        if self.date < dt.date.today():
            raise ValidationError({"date": ["Cannot create event in the past"]})

    def __str__(self):
        return f"TimeSlot(id={self.id}, on={self.event.id}, time={self.time}, date={self.date}"


class Participant(models.Model):
    # One user can be included in several groups.
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)
    # TODO: null=True needs to be removed before shippable product.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    ishost = models.BooleanField(default=False)

    def __str__(self):
        return f"user={self.user}, event={self.event}"


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


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    senttime = models.DateTimeField()
