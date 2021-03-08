# courses/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse
from django.contrib.auth.models import User


class CourseModelTest(TestCase):
    def setUp(self):
        self.golf = Event.objects.create(
            title="golfing",
            location="golf course",
            description=":)",
            starttime=dt.time(),
            endtime=dt.time(hour=2),
            startdate=dt.datetime.now(),
            enddate=dt.datetime.now() + dt.timedelta(days=1),
            duration=dt.timedelta(hours=2),
        )
        user = User.objects.create_user("tester", "myemail@test.com", "Elias123")

        self.client.login(username="tester", password="Elias123")

    def test_event_url_resolve_to_event_page(self):
        response = self.client.get(f"/event/{self.golf.id}/")
        self.assertTemplateUsed(response, "event.html")

    def test_context_has_the_event(self):
        # test if self.golf is part of the context
        response = self.client.get(f"/event/{self.golf.id}/")
        self.assertEqual(response.context["event"], self.golf)