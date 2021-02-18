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
    
    # def addparticipant(self, userID):



