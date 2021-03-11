from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from unittest import skip

class TimeSlotFunctionalTest(TestCase):
    def setUp(self):
        self.example_event_model = {
            "title": "golfing",
            "location": "golf course",
            "description": ":)",
            "starttime": dt.time(hour=8, minute=30),
            "endtime": dt.time(hour=11, minute=45),
            "startdate": dt.datetime.now(),
            "enddate": dt.datetime.now() + dt.timedelta(days=7),
            "duration": dt.timedelta(hours=1),
        }

        self.golf = Event.objects.create(**self.example_event_model)
        password = "Elias123"
        self.user = User.objects.create_user("tester", "myemail@test.com", password)

        self.client.login(username=self.user.username, password=password)
        self.tomorrow = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.example_timeslot = {
            "date": self.tomorrow,
            "time": "09:10"
        }

    def test_create_timeslot(self):
        response = self.client.post(f"/event/{self.golf.id}/", self.example_timeslot)
        # there is a timeslot in the context
        self.assertTrue(response.context["timeslots"])
        self.assertEqual(response.status_code, 200)

    def test_create_timeslot_in_the_past(self):
        timeslot = {
            "date": "1969-07-20",
            "time": "20:17",
        }
        response = self.client.post(f"/event/{self.golf.id}/", timeslot)
        # there is a timeslot in the context
        self.assertEqual(response.status_code, 400)

    @skip("Doesn't work right now")
    def test_create_timeslot_outside_range(self):
        # even't time interval is 8:30 to 11:45
        # posting timeslot at 13:00 should fail
        timeslot = {
            "date": self.tomorrow,
            "time": "13:00",
        }
        response = self.client.post(f"/event/{self.golf.id}/", timeslot)
        self.assertEqual(response.status_code, 400)

        # enddate is in one week. try posting timeslot in two weeks
        in_two_weeks = (dt.datetime.now() + dt.timedelta(days=14)).strftime("%Y-%m-%d")
        timeslot = {
            "date": in_two_weeks,
            "time": "09:10",
        }
        response = self.client.post(f"/event/{self.golf.id}/", timeslot)
        self.assertEqual(response.status_code, 400)