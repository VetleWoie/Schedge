from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse
from django.contrib.auth.models import User

PASSWORD = "Elias123"


class EventEditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", PASSWORD)
        self.client.login(username=self.user.username, password=PASSWORD)

        self.tomorrow = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.next_week = (dt.date.today() + dt.timedelta(days=7)).strftime("%Y-%m-%d")
        self.example_form = {
            "title": "hiking",
            "location": "mountains",
            "starttime": "05:00",
            "endtime": "23:00",
            "startdate": self.tomorrow,
            "enddate": self.next_week,
            "duration": ["0", "10", "0"],
        }
        response = self.client.post("/createevent/", self.example_form)
        self.event_id = "".join(c for c in response.url if c.isnumeric())

    def test_edit_changes_title(self):
        edited_event_form = self.example_form.copy()
        edited_event_form["title"] = "climbing"

        response = self.client.post(f"/event/{self.event_id}/edit/", edited_event_form)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/event/{self.event_id}/")

        self.assertEqual(response.context["event"].title, "climbing")
