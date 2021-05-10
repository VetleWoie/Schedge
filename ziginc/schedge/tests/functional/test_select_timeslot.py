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


        self.tomorrow = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.next_week = (dt.date.today() + dt.timedelta(days=7)).strftime("%Y-%m-%d")

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

    def test_select_timeslot(self):
        # create timeslot
        form = {"start_time": "06:00:00", "end_time": "20:00:00", "date":self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.guest.username, password=PASSWORD)

        form = {"start_time": "07:00:00", "end_time": "22:00:00", "date": self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.host.username, password=PASSWORD)

        self.assertEqual(2, TimeSlot.objects.all().count())
    
        form = {"options": "10:00,12:00,{}".format(self.tomorrow)}
        response = self.client.post(f"/event/{self.date.id}/select/", form)

        response = self.client.get(f"event/{self.date.id}/")
        date = Event.objects.get(id=self.date.id)
        self.assertTrue(date.chosen_time)
        # self.assertNotIn(response.context, "pts")
    
    def test_time_selected_wrong_method(self):
        """ Test notification when the host decides the time for an event"""

        # create timeslot
        form = {"start_time": "06:00:00", "end_time": "20:00:00", "date":self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.guest.username, password=PASSWORD)

        form = {"start_time": "07:00:00", "end_time": "22:00:00", "date": self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.host.username, password=PASSWORD)

        self.assertEqual(2, TimeSlot.objects.all().count())
    
        form = {"options": "10:00,20:00,{}".format(self.tomorrow)}
        response = self.client.get(f"/event/{self.date.id}/select/", form)
        self.assertEqual(response.status_code, 400)


    def test_selected_timeslot_unequal_to_duration(self):
        # create timeslot
        form = {"start_time": "06:00:00", "end_time": "20:00:00", "date":self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.guest.username, password=PASSWORD)

        form = {"start_time": "07:00:00", "end_time": "22:00:00", "date": self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.host.username, password=PASSWORD)

        self.assertEqual(2, TimeSlot.objects.all().count())
    
        form = {"options": "10:00,11:00,{}".format(self.tomorrow)}
        response = self.client.post(f"/event/{self.date.id}/select/", form)

        self.assertEqual(response.status_code, 400)
        # self.assertNotIn(response.context, "pts")
    
    def test_time_selected_event_not_legal_event(self):
        """ Test notification when the host decides the time for an event"""

        # create timeslot
        form = {"start_time": "06:00:00", "end_time": "20:00:00", "date":self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.guest.username, password=PASSWORD)

        form = {"start_time": "07:00:00", "end_time": "22:00:00", "date": self.tomorrow}
        self.client.post(f"/event/{self.date.id}/", form)

        self.client.login(username=self.host.username, password=PASSWORD)

        self.assertEqual(2, TimeSlot.objects.all().count())
    
        form = {"options": "10:00,20:00,{}".format(self.tomorrow)}
        non_existent_event = 9999999
        response = self.client.post(f"/event/{non_existent_event}/select/", form)
        self.assertEqual(response.status_code, 404)