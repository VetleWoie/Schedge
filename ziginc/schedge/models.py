from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.


class User(models.Model):
    userID = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)

class GroupEvent(models.Model):
    # One user can be included in several groups.
    userID = models.ForeignKey('User', on_delete=models.CASCADE)
    #TODO: null=True needs to be removed before shippable product.    
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True)


class Event(models.Model):
    
    title = models.CharField(max_length=100)
    # startDate = models.DateField()
    # endDate = models.DateField()
    # startTime = models.TimeField()
    # endTime = models.TimeField()
    duration = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    location = models.CharField(max_length=100)
    hostID = models.IntegerField()
    
    
    # def addparticipant(self, userID):



import datetime as dt
import django
# Create your models here.


class Event(models.Model):
    """The event model
    TODO: Add more stuff"""
    STATUS_OPTIONS = (
        ('C', 'Concluded'),
        ('U', 'Unresolved')
    )
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)

    starttime = models.TimeField(default=django.utils.timezone.now)
    endtime = models.TimeField(default=django.utils.timezone.now)

    startdate = models.DateField(default=django.utils.timezone.now)
    enddate = models.DateField(default=django.utils.timezone.now)

    duration = models.DurationField(max_length=dt.timedelta(hours=10), default=dt.timedelta())

    image = models.ImageField(default='default.jpg', upload_to='images/')
    status = models.CharField(max_length=10, default='U', choices=STATUS_OPTIONS)

class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()
    # creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        
