# courses/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse
from django.contrib.auth.models import User


class EventTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user("tester", "myemail@test.com", "Elias123")
        self.other = User.objects.create_user("Other", "othermail@test.com", "Elias123")
        
        self.example_model = {
            "title": "golfing",
            "location": "golf course",
            "description": ":)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=2),
            "startdate": dt.datetime.now(),
            "enddate": dt.datetime.now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
        }
        self.client.login(username=self.user.username, password="Elias123")
        self.golf = Event.objects.create(**self.example_model)
        self.golf.participants.add(self.user)


    def test_invalid_duration_field(self):
        with self.assertRaises(AttributeError):
            invalid_model = self.example_model.copy()
            invalid_model["duration"] = "This should be a timedelta"
            Event.objects.create(**invalid_model)

    def test_event_url_resolve_to_event_page(self):
        response = self.client.get(f"/event/{self.golf.id}/")
        self.assertTemplateUsed(response, "event.html")

    def test_context_has_the_event(self):
        # test if self.golf is part of the context
        response = self.client.get(f"/event/{self.golf.id}/")
        self.assertEqual(response.context["event"], self.golf)
    
    def test_invalid_id(self):
        invalid_event_id = 99999
        response = self.client.get(f"/event/{invalid_event_id}/")
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_user_not_access_to_event(self):
        self.client.logout()
        self.client.login(username=self.other.username, password='Elias123')
        response = self.client.get(f"/event/{self.golf.id}/")
        self.assertEqual(response.status_code, 401)

    def test_event_on_mypage(self):
        response = self.client.get(f"/mypage/")
        self.assertIn(self.golf, response.context["host_undecided"])
    
    def test_finished_event(self):
        old_event = self.example_model.copy()
        old_event["startdate"] = dt.datetime.now() - dt.timedelta(days=2)
        old_event["enddate"] = dt.datetime.now() - dt.timedelta(days=1)

        oldgolf = Event.objects.create(**old_event)
        oldgolf.participants.add(self.user)

        self.assertEqual(oldgolf.status, "U")
    
        response = self.client.get(f"/mypage/")
        self.assertNotIn(oldgolf, response.context["host_undecided"])
        oldgolf = Event.objects.get(id=oldgolf.id)
        self.assertEqual(oldgolf.status, "F")
    
    def test_finished_event_set_by_eventpage(self):
        # self.client.login(username=self.user.username, password="Elias123")
        old_event = self.example_model.copy()
        old_event["startdate"] = dt.datetime.now() - dt.timedelta(days=20)
        old_event["enddate"] = dt.datetime.now() - dt.timedelta(days=10)
        oldgolf = Event.objects.create(**old_event)
        oldgolf.participants.add(self.user)
    
        self.assertEqual(oldgolf.status, "U")
        response = self.client.get(f"/event/{oldgolf.id}/")
        self.assertEqual(response.status_code, 200)

        oldgolf = Event.objects.get(id=oldgolf.id)

        self.assertEqual(oldgolf.status, "F")
    