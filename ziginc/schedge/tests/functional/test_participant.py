from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip


class ParticipantTest(TestCase):
    def setUp(self):

        self.host = User.objects.create_user("host", "host@test.com", "Elias123")

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
        self.client.login(username=self.host.username, password="Elias123")

        # Make guest
        self.guest = User.objects.create_user("guest", "guest@test.com", "Elias123")
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
        self.guest2 = User.objects.create_user("guest2", "guest2@test.com", "Elias123")
        self.date.participants.add(self.guest2)

        self.client.logout()
        self.client.login(username=self.guest.username, password="Elias123")

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
        self.client.login(username=self.guest.username, password="Elias123")

        # Post request to delete host
        response = self.client.post(
            f"/event/{self.date.id}/participant_delete/{self.host.id}/"
        )
        self.assertEqual(response.status_code, 401)

        # Checking that the hosting participant is not deleted
        host = self.date.participants.get(id=self.host.id)
        self.assertTrue(host)
