from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite, Participant
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

        # Making hosting participant and login
        self.hosting_participant = Participant.objects.create(user=self.host, event=self.date, ishost=True)
        self.client.login(username=self.host.username, password="Elias123")

        # Making guest participant
        self.guest = User.objects.create_user("guest", "guest@test.com", "Elias123")
        self.guest_participant = Participant.objects.create(user=self.guest, event=self.date, ishost=False)
          
        
    def test_delete_guest_participant(self):
        """ Test for host deleting guest. """

        response = self.client.post(f"/participant_delete/{self.guest_participant.id}/")
        self.assertEqual(response.status_code, 302)

        # Checking that the guest participant is deleted
        with self.assertRaises(Participant.DoesNotExist):
            Participant.objects.get(id=self.guest_participant.id)

    # @skip("fji4fjo")
    def test_delete_hosting_participant(self):
        """ Test for the host trying to delete itself. """

        response = self.client.post(f"/participant_delete/{self.hosting_participant.id}/")
        self.assertEqual(response.status_code, 401)

        # Checking that the hosting participant is not deleted
        host = Participant.objects.get(id=self.hosting_participant.id)
        self.assertTrue(host)
    

    def test_unauthorized_guest_delete_guest(self):
        """ Test for one guest trying to delete another guest. """

        # Making a second guest
        self.guest2 = User.objects.create_user("guest2", "guest2@test.com", "Elias123")
        self.guest2_participant = Participant.objects.create(user=self.guest2, event=self.date, ishost=False)

        self.client.logout()
        self.client.login(username=self.guest.username, password="Elias123")

        # Deleting second guest
        response = self.client.post(f"/participant_delete/{self.guest2_participant.id}/")
        self.assertEqual(response.status_code, 401)

        # Checking that the second guest is not deleted
        guest2 = Participant.objects.get(id=self.guest2_participant.id)
        self.assertTrue(guest2)

    def test_unauthorized_guest_delete_host(self):
        """ Test for guest trying to delete host. """

        # Logging into guest account
        self.client.logout()
        self.client.login(username=self.guest.username, password="Elias123")

        # Post request to delete host
        response = self.client.post(f"/participant_delete/{self.hosting_participant.id}/")
        self.assertEqual(response.status_code, 401)

        # Checking that the hosting participant is not deleted
        host = Participant.objects.get(id=self.hosting_participant.id)
        self.assertTrue(host)
