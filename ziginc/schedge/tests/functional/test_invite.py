from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip

PASSWORD = "Elias123"


def as_other(func):
    """Log into other before the method and login back to me after.
    In case the test is from other's perspective"""
    def wrapper(*args, **kwargs):
        self = args[0]
        self.client.login(username=self.other.username, password=PASSWORD)
        func(*args, **kwargs)
        self.client.login(username=self.me.username, password=PASSWORD)

    return wrapper


class InviteTest(TestCase):
    def setUp(self):
        self.me = User.objects.create_user("Alice", "alice@test.com", PASSWORD)
        self.other = User.objects.create_user("Bob", "bob@test.com", PASSWORD)

        self.client.login(username=self.me.username, password=PASSWORD)

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
        self.example_model["title"] = "climbing"
        self.climbing = Event.objects.create(**self.example_model)
        self.hiking.participants.add(self.me)
        self.climbing.participants.add(self.me)

        # other invites me
        self.inv = Invite.objects.create(
            event=self.hiking,
            inviter=self.me,
            invitee=self.other,
            senttime=now(),
        )

    def test_invite(self):
        form = {"invitee": self.other.id}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)

        self.assertEqual(response.status_code, 302)
        invite = Invite.objects.get(event=self.climbing, inviter=self.me, invitee=self.other)
        self.assertTrue(invite)
        # timestamp should be within last 2 seconds
        # usually something like 0.03 s difference
        self.assertAlmostEqual(invite.senttime.timestamp(), now().timestamp(), delta=2.0)

    def test_invite_same_person_twice(self):
        form = {"invitee": self.other.id}

        first = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(first.status_code, 302)

        second = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(second.status_code, 400)

    def test_invite_yourself(self):
        form = {"invitee": self.me.id}

        response = self.client.post(f"/event/{self.hiking.id}/invite/", form)
        self.assertEqual(response.status_code, 400)

    @as_other
    def test_invite_is_on_mypage(self):
        response = self.client.get("/mypage/")
        # the invitation is on the mypage
        self.assertIn(self.inv, response.context["invites"])

    @as_other
    def test_accept_invitation(self):
        # other invites me
        response = self.client.post(f"/invite_accept/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)
        # other should be in the event's participants
        self.assertIn(self.other, self.hiking.participants.all())

    @as_other
    def test_reject_invitation(self):
        # other invites me
        response = self.client.post(f"/invite_reject/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)

        # other should not be participant
        self.assertNotIn(self.other, self.hiking.participants.all())

    def test_delete_invitation(self):
        response = self.client.post(f"/invite_delete/{self.inv.id}/")
        self.assertEqual(response.status_code, 302)

        # invite should no longer exist
        with self.assertRaises(Invite.DoesNotExist):
            Invite.objects.get(id=self.inv.id)

    def test_accept_someone_elses_invite(self):
        # me tries to accept other's invite
        response = self.client.post(f"/invite_accept/{self.inv.id}/")
        self.assertEqual(response.status_code, 401)

    def test_reject_someone_elses_invite(self):
        # me tries to reject other's invite
        response = self.client.post(f"/invite_reject/{self.inv.id}/")
        self.assertEqual(response.status_code, 401)

    @as_other
    def test_invite_as_not_attendee(self):
        form = {"invitee": self.me.id}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 401)

    def test_invite_unknown_user(self):
        form = {"invitee": 9000}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 400)

    def test_invite_with_get_method(self):
        form = {"invitee": self.other.id}
        response = self.client.get(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 400)