from django.contrib import admin
from .models import Event, TimeSlot, Invite, FriendRequest, Profile
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


# from .models import User
# Register your models here.
admin.site.register(Event)
admin.site.register(TimeSlot)
admin.site.register(Invite)
admin.site.register(FriendRequest)
admin.site.register(Profile)

# admin.site.register(User)
