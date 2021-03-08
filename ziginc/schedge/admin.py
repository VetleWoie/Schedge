from django.contrib import admin
from .models import Event, Participant, TimeSlot
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


# from .models import User
# Register your models here.
admin.site.register(Event)
admin.site.register(TimeSlot)
admin.site.register(Participant)

# admin.site.register(User)
