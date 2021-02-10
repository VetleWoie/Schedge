from django.db import models
import datetime as dt
# Create your models here.


class Event(models.Model):
    """The event model
    TODO: Add more stuff"""
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    # time = models.TimeField()
    # date = models.DateField()
    starttime = models.TimeField(default=dt.time())
    endtime = models.TimeField(default=dt.time())

    startdate = models.DateField(default=dt.datetime.now())
    enddate = models.DateField(default=dt.datetime.now())

    duration = models.DurationField(max_length=dt.timedelta(hours=10), default=dt.timedelta())

    image = models.ImageField(default='default.jpg', upload_to='images/')

class TimeSlot(models.Model):
    eventid = models.ForeignKey(Event, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()