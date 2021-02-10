from django.db import models
import datetime as dt
import django
# Create your models here.


class Event(models.Model):
    """The event model
    TODO: Add more stuff"""
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    # time = models.TimeField()
    # date = models.DateField()
    starttime = models.TimeField(default=django.utils.timezone.now)
    endtime = models.TimeField(default=django.utils.timezone.now)

    startdate = models.DateField(default=django.utils.timezone.now)
    enddate = models.DateField(default=django.utils.timezone.now)

    duration = models.DurationField(max_length=dt.timedelta(hours=10), default=dt.timedelta())

    image = models.ImageField(default='default.jpg', upload_to='images/')

class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()
    # creator = models.ForeignKey(User, on_delete=models.CASCADE)
