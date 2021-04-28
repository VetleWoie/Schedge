from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.utils.timezone import now
from unittest import skip

PASSWORD = "Elias123"


def as_bob(func):
    """Log into bob before the method and login back to alice after.
    In case the test is from Bob's perspective"""
    def wrapper(*args, **kwargs):
        self = args[0]
        self.client.login(username=self.bob.username, password=PASSWORD)
        func(*args, **kwargs)
        self.client.login(username=self.alice.username, password=PASSWORD)

    return wrapper


class InviteTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("Alice", "alice@test.com", PASSWORD)
        self.bob = User.objects.create_user("Bob", "bob@test.com", PASSWORD)

        self.client.login(username=self.alice.username, password=PASSWORD)

        self.example_model = {
            "title": "hiking",
            "location": "mount everest",
            "description": ":)",
            "starttime": dt.time(),
            "endtime": dt.time(hour=14),
            "startdate": now(),
            "enddate": now() + dt.timedelta(days=1),
            "duration": dt.timedelta(hours=2),
            "host": self.alice,
        }

        self.hiking = Event.objects.create(**self.example_model)
        self.example_model["title"] = "climbing"
        self.climbing = Event.objects.create(**self.example_model)
        self.hiking.participants.add(self.alice)
        self.climbing.participants.add(self.alice)

        # other invites me
        self.inv = Invite.objects.create(
            event=self.hiking,
            inviter=self.alice,
            invitee=self.bob,
            senttime=now(),
        )

    def test_invite(self):
        form = {"invitee": self.bob.id}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)

        self.assertEqual(response.status_code, 302)
        invite = Invite.objects.get(event=self.climbing, inviter=self.alice, invitee=self.bob)
        self.assertTrue(invite)
        # timestamp should be within last 2 seconds
        # usually something like 0.03 s difference
        self.assertAlmostEqual(invite.senttime.timestamp(), now().timestamp(), delta=2.0)

    def test_invite_same_person_twice(self):
        form = {"invitee": self.bob.id}

        first = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(first.status_code, 302)

        second = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(second.status_code, 400)

    def test_invite_yourself(self):
        form = {"invitee": self.alice.id}

        response = self.client.post(f"/event/{self.hiking.id}/invite/", form)
        self.assertEqual(response.status_code, 400)

    @as_bob
    def test_invite_is_on_mypage(self):
        response = self.client.get("/mypage/")
        # the invitation is on the mypage
        self.assertIn(self.inv, response.context["invites"])

    @as_bob
    def test_accept_invitation(self):
        # bob accept invite
        response = self.client.post(f"/invite_accept/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)
        # other should be in the event's participants
        self.assertIn(self.bob, self.hiking.participants.all())

    @as_bob
    def test_accepted_invitation_is_on_mypage(self):
        # bob accept invite
        self.client.post(f"/invite_accept/{self.inv.id}/")
        # the accepting should redirect
        response = self.client.get("/mypage/")
        self.assertIn(self.hiking, response.context["participant_as_guest"])

    @as_bob
    def test_rejected_invitation_is_not_on_mypage(self):
        # bob reject invite
        self.client.post(f"/invite_reject/{self.inv.id}/")
        # the accepting should redirect
        response = self.client.get("/mypage/")
        self.assertNotIn(self.hiking, response.context["participant_as_guest"])
 

    @as_bob
    def test_reject_invitation(self):
        # bob reject invite
        response = self.client.post(f"/invite_reject/{self.inv.id}/")
        # the accepting should redirect
        self.assertEqual(response.status_code, 302)

        # other should not be participant
        self.assertNotIn(self.bob, self.hiking.participants.all())

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

    @as_bob
    def test_invite_someone_as_not_attendee(self):
        form = {"invitee": self.alice.id}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 401)

    def test_invite_unknown_user(self):
        form = {"invitee": 9000}
        response = self.client.post(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 400)

    def test_invite_with_get_method(self):
        form = {"invitee": self.bob.id}
        response = self.client.get(f"/event/{self.climbing.id}/invite/", form)
        self.assertEqual(response.status_code, 400)
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
    
    def test_pending_invites_as_host(self):
        # Check that the host is able to see pending invites
        response = self.client.get(f"/event/{self.hiking.id}/")
        self.assertContains(response, "id='pending_invites'")
    
    def test_invisible_pending_invites_as_guest(self):
        # Check that an attendee is not able to see pending invites.
        self.client.logout()
        self.client.login(username=self.other.username, password='Elias123')
        response = self.client.get(f"/event/{self.hiking.id}/")
        self.assertNotContains(response, "id='pending_invites'")
    

