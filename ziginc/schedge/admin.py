from django.contrib import admin
from .models import Event
from .models import GroupEvent
from .models import User

# Register your models here.
admin.site.register(Event)
admin.site.register(GroupEvent)
admin.site.register(User)