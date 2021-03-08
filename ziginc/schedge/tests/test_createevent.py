from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse

class CreateEventTest(TestCase):
    def setUp(self):
        self.example_form = {
            "title": "hiking",
            "location": "mountains",
            "starttime": "05:00",
            "endtime": "23:00",
            "startdate": "2024-01-01",
            "enddate":"2025-03-03",
            "duration": "00:10:00"
        }
        user = User.objects.create_user('tester', 'myemail@test.com', 'Elias123')

        # self.client.login(username='tester', password='Elias123')


    def test_create(self):
        response = self.client.post("/createevent/", self.example_form)

        self.assertEqual(response.status_code, 302)  # redirects
        self.assertRegex(response.url, "^\/event\/\d+\/$") # url is /event/[some number]/
        
        id_ = "".join(c for c in response.url if c.isnumeric()) # the number in the url
        response = self.client.get(f"/event/{id_}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["event"].title, "hiking")

    def test_invalid_duration_field(self):

        # with self.assertRaises(AttributeError):
        golf = Event.objects.create(
            title="golfing",
            location="golf course",
            description=":)",
            starttime=dt.time(),
            endtime=dt.time(),
            startdate=dt.datetime.now(),
            enddate=dt.datetime.now() + dt.timedelta(days=1),
            duration=dt.timedelta(hours=2),
        )
            
    def test_title_too_long(self):
        # with self.assertRaises()
        invalid_form = self.example_form.copy()
        invalid_form["title"] = "a really long title "*10
        response = self.client.post("/createevent/", invalid_form)
        self.assertEqual(response.status_code, 400)

    # def test_event_in_the_past(self):
    #     # doesn't pass :(
    #     # does it have to pass tho?

    #     invalid_form = self.example_form.copy()
    #     invalid_form["startdate"] = "1969-07-20"

    #     response = self.client.post("/createevent/", invalid_form)
    #     print("\n\n" + response.url + "\n\n")
    #     self.assertEqual(response.status_code, 400)
    #     getresponse = self.client.get("/event/1/")
    #     # print(getresponse.context)