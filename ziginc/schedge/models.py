from django.db import models
import datetime as dt
from django.contrib.auth.models import User
import django


import uuid
# Create your models here.

class Event(models.Model):
    """The event model
    TODO: Add more stuff"""
    STATUS_OPTIONS = (
        ('C', 'Concluded'),
        ('U', 'Unresolved')
    )
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True, max_length=500)

    starttime = models.TimeField(default=django.utils.timezone.now)
    endtime = models.TimeField(default=django.utils.timezone.now)

    startdate = models.DateField(default=django.utils.timezone.now)
    enddate = models.DateField(default=django.utils.timezone.now)

    duration = models.DurationField(max_length=dt.timedelta(hours=10), default=dt.timedelta())

    image = models.ImageField(default='default.jpg', upload_to='images/')
    status = models.CharField(max_length=10, default='U', choices=STATUS_OPTIONS)
    host = models.ForeignKey(User, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return f"Event(id={self.id}, title={self.title}, ...)"

class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()
    # creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"TimeSlot(id={self.id}, on={self.event.id}, time={self.time}, date={self.date}"



class GroupEvent(models.Model):
    # One user can be included in several groups.
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    #TODO: null=True needs to be removed before shippable product.    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    ishost = models.BooleanField(default=False)

    def __str__(self):
        return f"user={self.user}, event={self.event}"
