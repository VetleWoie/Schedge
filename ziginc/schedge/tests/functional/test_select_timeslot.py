from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip

PASSWORD = "Elias123"


class SelectTimeslotTest(TestCase):
    def setUp(self):

        self.host = User.objects.create_user("host", "host@test.com", PASSWORD)

        self.example_model = {
            "title": "date night",
            "location": "the lightning route",
            "description": ";)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=14),
            "startdate": now(),
            "enddate": now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
            "host": self.host,
        }
        self.date = Event.objects.create(**self.example_model)

        self.date.participants.add(self.host)
        self.client.login(username=self.host.username, password=PASSWORD)

        # Make guest
        self.guest = User.objects.create_user("guest", "guest@test.com", PASSWORD)
        self.date.participants.add(self.guest)

    
    # def 