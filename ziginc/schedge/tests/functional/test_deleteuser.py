from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm
from unittest import skip
import datetime as dt
from django.utils.timezone import now
from schedge.models import Event
from schedge.model_utils import create_time_slot
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
        """
        1. Create a user
        2. Login user
        3. Delete user
        4. Assert that user is deleted from database.
        """
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        self.client.post("/mypage/delete_user_account/")

        usr_exists = User.objects.filter(username=self.userGood["username"]).exists()
        self.assertEqual(usr_exists, False)

    @skip("Need the home view which is not present in this version of master, but which is implemented in another branch.")
    def test_delete_user_redirect(self):
        """
        1. Create a user
        2. Login user
        3. Delete user
        4. Assert that the redirection takes us to home page (not yet implemented)
        """
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        response2 = self.client.post("/mypage/delete_user_account/")
        self.assertEqual(response2.url, "/home/")

    def test_delete_event_host(self):
        """
        1. Create a user
        2. Login user
        3. Create event where user is host
        4. Delete user
        5. Assert that the event is no longer present due to cascade.
        """
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)
        
        usr = User.objects.get(username=self.userGood['username'])
        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

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

        self.client.post("/mypage/delete_user_account/")

        del_event = Event.objects.filter(id=self.date.id).exists()
        self.assertEqual(del_event, False)

    def test_delete_event_host_with_timeslot(self):
        """
        1. Create a user1
        2. Create user2
        3. Login user1
        4. Create event where user1 is host
        5. Invite user2
        6. Create and add timeslot from user2 to event.
        7. Assert that the timeslot is present on the event.
        8. Logout user1 and login user 2.
        9. Delete user2 (The owner of the timeslot)
        5. Assert that the timeslot is no longer present in the event due to cascading.
        """
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)
        usr = User.objects.get(username=self.userGood['username'])
        
        self.client.login(username="host", password="Elias123")

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

        self.date.participants.add(usr)

        form = {"invitee": usr.id}
        response = self.client.post(f"/event/{self.date.id}/invite/", form)
        self.assertEqual(response.status_code, 302)

        t1 = {
            "start_time": dt.time(8,00,00),
            "end_time": dt.time(10,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date()
        }
        
        create_time_slot(self.date, usr, t1)

        n_timeslots = TimeSlot.objects.filter(event=self.date)
        self.assertEqual(len(n_timeslots), 1)

        self.client.logout()
        self.client.login(username=self.userGood['username'], password=self.userGood['password'])        
        
        self.client.post("/mypage/delete_user_account/")

        n_timeslots = TimeSlot.objects.filter(event=self.date)
        self.assertEqual(len(n_timeslots),0)        
