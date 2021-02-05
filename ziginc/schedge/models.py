from django.db import models

# Create your models here.


class Event(models.Model):
    title = models.CharField(max_length=100)
    startDate = models.DateField()
    enddate = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    duration = models.DurationField()
    description = models.CharField(max_length=500)
    location = models.CharField(max_length=100)
    # hostID = models.ForeignKey()
    # groupID = models.ForeignKey()