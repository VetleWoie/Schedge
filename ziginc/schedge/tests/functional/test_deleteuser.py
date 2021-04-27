from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm
from unittest import skip
import datetime as dt
from django.utils.timezone import now
from schedge.models import Event

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

    # TODO: Create event -> delete user -> see that event is also deleted.
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

        del_event = Event.objects.filter(host=usr).exists()

        self.assertEqual(del_event, False)





    # TODO: Create timeslot -> delete user -> see that timeslot is removed.
    # TODO: Create event -> invite guest -> delete user -> check if participant has access to event(shoulnd't).