from django.db import models

import datetime as dt
import django

from django.contrib.auth import get_user_model

# Create your models here.


class Event(models.Model):
    """The event model
    TODO: Add more stuff"""

    STATUS_OPTIONS = (("C", "Concluded"), ("U", "Unresolved"))
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True, max_length=500)

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

    def __str__(self):
        return f"Event(id={self.id}, title={self.title}, ...)"


class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ["event", "start_time", "end_time", "date"]

    def __str__(self):
        return f"TimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}"

class PotentialTimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    participants = models.IntegerField()

    def __str__(self):
        return f"PotentialTimeSlot(id={self.id}, on={self.event.id}, start_time={self.start_time}, end_time={self.end_time}, date={self.date}, participants={self.participants}"
    

class Participant(models.Model):
    # One user can be included in several groups.
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default=1)
    # TODO: null=True needs to be removed before shippable product.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    ishost = models.BooleanField(default=False)

    def __str__(self):
        return f"user={self.user}, event={self.event}"
