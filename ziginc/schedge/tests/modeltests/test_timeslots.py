from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse


class TimeSlotModelTest(TestCase):
    def setUp(self):
        self.example_event_model = {
            "title": "golfing",
            "location": "golf course",
            "description": ":)",
            "starttime": dt.time(hour=8, minute=30),
            "endtime": dt.time(hour=11, minute=45),
            "startdate": dt.datetime.now(),
            "enddate": dt.datetime.now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=1),
        }

        self.golf = Event.objects.create(**self.example_event_model)
        password = "Elias123"
        self.user = User.objects.create_user("tester", "myemail@test.com", password)

        self.client.login(username=self.user.username, password=password)


    def test_create_timeslot(self):
        self.example_timeslot = {
            "event": self.golf,
            "creator": self.user,
            "date": dt.datetime.now() + dt.timedelta(days=2),
            "time": dt.time(hour=9, minute=0)
        }

        timeslot = TimeSlot(**self.example_timeslot)
        self.assertEqual(timeslot.event, self.golf)

