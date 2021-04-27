from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm
from unittest import skip
import datetime as dt
from django.utils.timezone import now
from schedge.models import Event
from schedge.utils import create_time_slot
from schedge.models import Event, TimeSlot

class DeleteUserTest(TestCase):
    def setUp(self):

        self.host = User.objects.create_user("host", "host@test.com", "Elias123")

        self.userGood = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }
        self.other = {
            "username" : "test1",
            "first_name" : "Test1",
            "last_name" : "ing1",
            "email" : "test1@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }

        

    def test_delete_user(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        self.client.post("/mypage/delete_user_account/")

        # Check that user does not exists after deletion.
        usr_exists = User.objects.filter(username=self.userGood["username"]).exists()
        self.assertEqual(usr_exists, False)

    @skip("Need the home view which is not present in this version of master, but which is implemented in another branch.")
    def test_delete_user_redirect(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        response2 = self.client.post("/mypage/delete_user_account/")
        self.assertEqual(response2.url, "/home/")

    def test_delete_event_host(self):
        # CREATE USER
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)
        
        usr = User.objects.get(username=self.userGood['username'])
        # LOGIN USER
        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        # CREATE EVENT
        self.example_model = {
            "title": "date night",
            "location": "the lightning route",
            "description": ";)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=14),
            "startdate": now(),
            "enddate": now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
            "host": usr,
        }
        
        self.date = Event.objects.create(**self.example_model)

        self.date.participants.add(usr)

        # DELETE USER/HOST
        self.client.post("/mypage/delete_user_account/")

        del_event = Event.objects.filter(id=self.date.id).exists()

        self.assertEqual(del_event, False)

    def test_delete_event_host_with_timeslot(self):
        # CREATE USER
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)
        usr = User.objects.get(username=self.userGood['username'])
        
        # CREATE OTHER USER
        response_other = self.client.post("/signup/", self.other)
        self.assertEqual(response_other.status_code, 302)
        other = User.objects.get(username=self.other['username'])
        
        # LOGIN USER
        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        # CREATE EVENT
        self.example_model = {
            "title": "date night",
            "location": "the lightning route",
            "description": ";)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=14),
            "startdate": now(),
            "enddate": now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
            "host": usr,
        }
        self.date = Event.objects.create(**self.example_model)

        self.date.participants.add(usr)

        # INVITE OTHER USER
        form = {"invitee": other.id}
        response = self.client.post(f"/event/{self.date.id}/invite/", form)
        self.assertEqual(response.status_code, 302)

        # CREATE TIMESLOT FOR 'OTHER'
        t1 = {
            "start_time": dt.time(8,00,00),
            "end_time": dt.time(10,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date()
        }
        
        create_time_slot(self.date, other, t1)

        n_timeslots = TimeSlot.objects.filter(event=self.date)
        self.assertEqual(len(n_timeslots),1)

        self.client.logout()
        self.client.login(username=self.other['username'], password=self.other['password'])        
        
        # DELETE 'OTHER'
        self.client.post("/mypage/delete_user_account/")

        n_timeslots = TimeSlot.objects.filter(event=self.date)
        self.assertEqual(len(n_timeslots),0)        
