from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip


class InviteTest(TestCase):
    def setUp(self):
        self.me = User.objects.create_user("Alice", "alice@test.com", "Elias123")
        self.other = User.objects.create_user("Bob", "bob@test.com", "Elias123")

        self.client.login(username=self.me.username, password="Elias123")

        self.example_model = {
            "title": "hiking",
            "location": "mount everest",
            "description": ":)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=14),
            "startdate": now(),
            "enddate": now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
            "host": self.me,
        }

        self.hiking = Event.objects.create(**self.example_model)

        # other invites me
        self.inv = Invite.objects.create(
            event=self.hiking,
            inviter=self.other,
            invitee=self.me,
            senttime=now(),
        )

    def test_invite(self):
        form = {"invitee": self.other.id}
        response = self.client.post(f"/event/{self.hiking.id}/invite/", form)

        self.assertEqual(response.status_code, 302)

    def test_invite_same_person_twice(self):
        form = {"invitee": self.other.id}

        first = self.client.post(f"/event/{self.hiking.id}/invite/", form)
        self.assertEqual(first.status_code, 302)

        second = self.client.post(f"/event/{self.hiking.id}/invite/", form)
        self.assertEqual(second.status_code, 400)

    def test_invite_yourself(self):
        form = {"invitee": self.me.id}

        response = self.client.post(f"/event/{self.hiking.id}/invite/", form)
        self.assertEqual(response.status_code, 400)


    def test_invite_is_on_mypage(self):
        response = self.client.get("/mypage/")
        # the invitation is on the mypage
        self.assertIn(self.inv, response.context["invites"])

    def test_accept_invitation(self):
        # other invites me
        response = self.client.get(f"/invite_accept/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)

    def test_reject_invitation(self):
        # other invites me
        response = self.client.get(f"/invite_reject/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)

    def test_delete_invitation(self):
        
        response = self.client.post(f"/invite_delete/{self.inv.id}/")
        self.assertEqual(response.status_code, 302)
        
        with self.assertRaises(Invite.DoesNotExist):
            Invite.objects.get(id=self.inv.id)
    
    def test_invite_only_as_host(self):
        response = self.client.get(f"/event/{self.hiking.id}/")
        self.assertContains(response, 'id="Invite_box"')
    
    def test_try_invite_as_invitee(self):
        # Logout as host user and log in as another invitee.
        self.client.logout()
        self.client.login(username=self.other.username, password="Elias123")

        # Make sure the invited person does not have access to invite others.
        response = self.client.get(f"/event/{self.hiking.id}/")
        self.assertNotContains(response, 'id="Invite_box')
        
        self.client.logout()
        self.client.login(username=self.me.username, password='Elias123')

