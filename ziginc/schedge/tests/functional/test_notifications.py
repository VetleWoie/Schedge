from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, Invite
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from notifications.models import Notification
from unittest import skip


PASSWORD = "Elias123"

class NotificationTest(TestCase):
    def setUp(self):
        self.inviter = User.objects.create_user(
            "inviter", "inviter@test.com", PASSWORD
        )
        self.invitee = User.objects.create_user(
            "invitee", "invitee@test.com", PASSWORD
        )
        self.client.login(username=self.inviter.username, password=PASSWORD)
        
        self.tomorrow = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.next_week = (dt.date.today() + dt.timedelta(days=7)).strftime("%Y-%m-%d")
        self.example_form = {
            "title": "hiking",
            "location": "mountains",
            "starttime": "05:00",
            "endtime": "23:00",
            "startdate": self.tomorrow,
            "enddate": self.next_week,
            "duration": ["0", "10", "0"],
        }
        response = self.client.post("/createevent/", self.example_form)
        
        self.event_id = "".join(c for c in response.url if c.isnumeric())
        self.invite_form = {"invitee": str(self.invitee.id)}
        self.client.post(f"/event/{self.event_id}/invite/", self.invite_form)


    def test_gets_notification_on_invite(self):
        # assert invitee has an invitation
        notifications = Notification.objects.filter(recipient=self.invitee)
        # invitee should have 1 notification
        self.assertEqual(1, len(notifications))

        notification = notifications[0]
        self.assertEqual(notification.actor, self.inviter)
        self.assertEqual(notification.verb, "invite")
        self.assertEqual(notification.data["title"], "hiking")
        self.assertEqual(notification.data["url"], str(self.event_id))
        self.assertEqual(notification.target, Event.objects.get(id=self.event_id))

    def test_gets_notification_on_invite_accept(self):
        invite = Invite.objects.get(inviter=self.inviter)
        self.client.logout()
        self.client.login(username=self.invitee.username, password=PASSWORD)

        response = self.client.post(f"/invite_accept/{invite.id}/")        # assert invitee has an invitation
        notifications = Notification.objects.filter(recipient=self.inviter)
        # invitee should have 1 notification
        self.assertEqual(1, len(notifications))

        notification = notifications[0]
        self.assertEqual(notification.actor, self.invitee)
        self.assertEqual(notification.verb, "invite accept")
        self.assertEqual(notification.data["title"], "hiking")
        self.assertEqual(notification.data["url"], str(self.event_id))
        self.assertEqual(notification.target, Event.objects.get(id=self.event_id))
    
    def test_gets_notification_on_invite_reject(self):
        invite = Invite.objects.get(inviter=self.inviter)
        self.client.logout()
        self.client.login(username=self.invitee.username, password=PASSWORD)

        response = self.client.post(f"/invite_reject/{invite.id}/")
        notifications = Notification.objects.filter(recipient=self.inviter)
        # invitee should have 1 notification
        self.assertEqual(1, len(notifications))

        notification = notifications[0]
        self.assertEqual(notification.actor, self.invitee)
        self.assertEqual(notification.verb, "invite reject")
        self.assertEqual(notification.data["title"], "hiking")
        self.assertEqual(notification.data["url"], str(self.event_id))
        self.assertEqual(notification.target, Event.objects.get(id=self.event_id))