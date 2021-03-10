from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains


class CreateEventTest(TestCase):
    def setUp(self):
        self.tomorrow = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.next_week = (dt.date.today() + dt.timedelta(days=7)).strftime("%Y-%m-%d")
        self.example_form = {
            "title": "hiking",
            "location": "mountains",
            "starttime": "05:00",
            "endtime": "23:00",
            "startdate": self.tomorrow,
            "enddate": self.next_week,
            "duration": "00:10:00",
        }
        user = User.objects.create_user("tester", "myemail@test.com", "Elias123")

        self.client.login(username="tester", password="Elias123")

    def test_create(self):
        response = self.client.post("/createevent/", self.example_form)

        self.assertEqual(response.status_code, 302)  # redirects
        self.assertRegex(
            response.url, "^\/event\/\d+\/$"
        )  # url is /event/[some number]/

        # the number in the url
        id_ = "".join(c for c in response.url if c.isnumeric())
        response = self.client.get(f"/event/{id_}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "event.html")
        self.assertEqual(response.context["event"].title, "hiking")

    def test_title_too_long(self):
        invalid_form = self.example_form.copy()
        invalid_form["title"] = "a really long title " * 10

        response = self.client.post("/createevent/", invalid_form)
        self.assertTemplateNotUsed(response, "event.html")  # didn't create event

    def test_invalid_duration_field(self):
        invalid_form = self.example_form.copy()
        invalid_form["duration"] = "this is not a proper duration"

        response = self.client.post("/createevent/", invalid_form)
        self.assertTemplateNotUsed(response, "event.html")  # didn't create event

    def test_event_in_the_past(self):
        invalid_form = self.example_form.copy()
        invalid_form["startdate"] = "1969-07-20"

        response = self.client.post("/createevent/", invalid_form)
        self.assertTemplateNotUsed(response, "event.html")  # didn't create event

    def test_event_too_short(self):
        # dancing takes 2 hours, but time between start and end is 1 hour
        invalid_form = {
            "title": "dancing",
            "location": "dance floor",
            "starttime": "17:00",
            "endtime": "18:00",
            "startdate": self.tomorrow,
            "enddate": self.tomorrow,
            "duration": "02:00:00",
        }

        response = self.client.post("/createevent/", invalid_form)
        self.assertTemplateNotUsed(response, "event.html")  # didn't create event
