from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse
from django.contrib.auth.models import User
import os

PASSWORD = "Elias123"


class EventEditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user", "user@test.com", PASSWORD)
        self.other = User.objects.create_user("other", "user@test.com", PASSWORD)
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

    def test_edit_image(self):
        with open("schedge/tests/mandrill.jpg", "rb") as fp:
            edited_event_form = self.example_form.copy()
            edited_event_form["image"] = fp
            response = self.client.post(
                f"/event/{self.event_id}/edit/", edited_event_form
            )

        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/event/{self.event_id}/")

        imgurl = response.context["event"].image.url
        self.assertRegex(imgurl, r"^\/media\/images\/mandrill.*\.jpe?g$")

        # delete the new file
        # remove the initial slash to make it a relative path
        os.remove(imgurl[1:])
    
    def test_try_edit_invalid_event(self):
        edited_event_form = self.example_form.copy()
        edited_event_form["title"] = "climbing"
        non_existent_event = 9999999
        response = self.client.post(f"/event/{non_existent_event}/edit/", edited_event_form)
        self.assertEqual(response.status_code, 404)

    
    def test_edit_event_not_as_host(self):
        edited_event_form = self.example_form.copy()
        edited_event_form["title"] = "climbing"

        self.client.logout()
        self.client.login(username=self.other.username, password=PASSWORD)

        response = self.client.post(f"/event/{self.event_id}/edit/", edited_event_form)
        self.assertEqual(response.status_code, 401)

    def test_invalid_form(self):

        self.invalid_form = {
            "location": "Ocean",
            "starttime": "05:00",
            "endtime": "23:00",
            "startdate": self.tomorrow,
            "enddate": self.next_week,
            "duration": ["0", "5", "0"],
        }

        response = self.client.post(f"/event/{self.event_id}/edit/", self.invalid_form)
        self.assertEqual(response.status_code, 400)
    
    def test_delete_invalid_event(self):
        invalid_event_id = 9999999999999999
        response = self.client.post(f"/event/{invalid_event_id}/edit/delete/")
        self.assertEqual(response.status_code, 404)


    def test_delete_event_wrong_method(self):
        edited_event_form = self.example_form.copy()
        edited_event_form["title"] = "climbing"

        response = self.client.get(f"/event/{self.event_id}/edit/delete/", edited_event_form)
        self.assertEqual(response.status_code, 400)

    def test_delete_event_not_as_host(self):
        self.client.logout()
        self.client.login(username=self.other.username, password=PASSWORD)

        response = self.client.post(f"/event/{self.event_id}/edit/delete/")
        self.assertEqual(response.status_code, 401)