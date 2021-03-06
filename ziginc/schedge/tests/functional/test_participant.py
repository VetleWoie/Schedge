from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip

PASSWORD = "Elias123"


def as_guest(func):
    """Log into bob before the method and login back to alice after.
    In case the test is from Bob's perspective"""

    def wrapper(*args, **kwargs):
        self = args[0]
        self.client.login(username=self.guest.username, password=PASSWORD)
        func(*args, **kwargs)
        self.client.login(username=self.host.username, password=PASSWORD)

    return wrapper


class ParticipantTest(TestCase):
    def setUp(self):

        self.host = User.objects.create_user("host", "host@test.com", PASSWORD)

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

    def test_delete_guest_participant(self):
        """ Test for host deleting guest. """

        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{self.guest.id}/"
        )
        self.assertEqual(response.status_code, 302)

        # Checking that the guest participant is deleted
        with self.assertRaises(User.DoesNotExist):
            self.date.participants.get(id=self.guest.id)

    def test_delete_hosting_participant(self):
        """ Test for the host trying to delete itself. """

        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{self.host.id}/"
        )
        self.assertEqual(response.status_code, 401)

        # Checking that the hosting participant is not deleted
        host = self.date.participants.get(id=self.host.id)
        self.assertTrue(host)

    def test_unauthorized_guest_delete_guest(self):
        """ Test for one guest trying to delete another guest. """

        # Making a second guest
        self.guest2 = User.objects.create_user("guest2", "guest2@test.com", PASSWORD)
        self.date.participants.add(self.guest2)

        self.client.logout()
        self.client.login(username=self.guest.username, password=PASSWORD)

        # Deleting second guest
        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{self.guest.id}/"
        )
        self.assertEqual(response.status_code, 401)

        # Checking that the second guest is not deleted
        guest2 = self.date.participants.get(id=self.guest2.id)
        self.assertTrue(guest2)

    def test_unauthorized_guest_delete_host(self):
        """ Test for guest trying to delete host. """

        # Logging into guest account
        self.client.logout()
        self.client.login(username=self.guest.username, password=PASSWORD)

        # Post request to delete host
        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{self.host.id}/"
        )
        self.assertEqual(response.status_code, 401)

        # Checking that the hosting participant is not deleted
        host = self.date.participants.get(id=self.host.id)
        self.assertTrue(host)

    @as_guest
    def test_participant_leave(self):
        resp = self.client.post(f"/event/{self.date.id}/participant_leave/{self.guest.id}/")
        self.assertNotIn(self.guest, self.date.participants.all())

    @as_guest
    def test_participant_leave_non_existent_event(self):
        non_existing_event = 99999
        response = self.client.post(f"/event/{non_existing_event}/participant_leave/{self.guest.id}/")
        self.assertEqual(response.status_code, 404)

    @as_guest
    def test_participant_leave_wrong_method(self):
        response = self.client.get(f"/event/{self.date.id}/participant_leave/{self.guest.id}/")
        self.assertEqual(response.status_code, 400)

    def test_participant_leave_non_existing_user(self):
        non_existing_user_id = 9999999
        response = self.client.post(f"/event/{self.date.id}/participant_leave/{non_existing_user_id}/")
        self.assertEqual(response.status_code, 404)
    

    def test_delete_participant_from_non_existing_event(self):
        """ Test for host deleting guest. """
        non_existing_event = 99999
        response = self.client.post(
            f"/event/{non_existing_event}/participant_delete/{self.guest.id}/"
        )
        self.assertEqual(response.status_code, 404)

        
    def test_delete_guest_participant_wrong_method(self):
        """ Test for deleting guest using wrong method. """

        response = self.client.get(
            f"/event/{self.date.id}/participant_delete/{self.guest.id}/"
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_guest_that_is_not_participant(self):
        """ Test for deleting guest that is not a participant. """
        non_participating_guest_id = 9999999
        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{non_participating_guest_id}/"
        )
        self.assertEqual(response.status_code, 404)