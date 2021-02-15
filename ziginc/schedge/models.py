from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.


class User(models.Model):
    userID = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

class GroupEvent(models.Model):
    # One user can be included in several groups.
    userID = models.IntegerField()
    # GroupID == eventid to see who is in the same group (going to the same event)
    groupID = models.IntegerField()


class Event(models.Model):
    STATUS_OPTIONS = (
        ('C', 'Concluded'),
        ('U', 'Unresolved')
    )
    title = models.CharField(max_length=100)
    # startDate = models.DateField()
    # endDate = models.DateField()
    # startTime = models.TimeField()
    # endTime = models.TimeField()
    duration = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    location = models.CharField(max_length=100)
    hostID = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_OPTIONS)
    # groupID = models.ForeignKey()

