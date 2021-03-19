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
        self.inviter = User.objects.create_user("inviter", "inviter@test.com", PASSWORD)
        self.invitee = User.objects.create_user("invitee", "invitee@test.com", PASSWORD)
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
        self.assertEqual(notification.data["url"], f"/event/{self.event_id}/")
        self.assertEqual(
            notification.target,
            Invite.objects.get(inviter=self.inviter, invitee=self.invitee),
        )

    def test_gets_notification_on_invite_accept(self):
        invite = Invite.objects.get(inviter=self.inviter)
        self.client.logout()
        self.client.login(username=self.invitee.username, password=PASSWORD)

        response = self.client.post(f"/invite_accept/{invite.id}/")
        # assert invitee has an invitation
        notifications = Notification.objects.filter(recipient=self.inviter)
        # invitee should have 1 notification
        self.assertEqual(1, len(notifications))

        notification = notifications[0]
        self.assertEqual(notification.actor, self.invitee)
        self.assertEqual(notification.verb, "invite accepted")
        self.assertEqual(notification.data["title"], "hiking")
        self.assertEqual(notification.data["url"], f"/event/{self.event_id}/")
        self.assertIs(notification.target, None)

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
        self.assertEqual(notification.verb, "invite rejected")
        self.assertEqual(notification.data["title"], "hiking")
        self.assertEqual(notification.data["url"], f"/event/{self.event_id}/")
        self.assertIs(notification.target, None)

    def test_accept_marks_notification_as_read(self):
        invite = Invite.objects.get(inviter=self.inviter)
        self.client.login(username=self.invitee.username, password=PASSWORD)
        response = self.client.post(f"/invite_accept/{invite.id}/")
        self.assertFalse(
            Notification.objects.filter(recipient=self.invitee).unread().exists()
        )
        self.assertTrue(
            Notification.objects.filter(recipient=self.invitee).read().exists()
        )

    def test_reject_marks_notification_as_read(self):
        invite = Invite.objects.get(inviter=self.inviter)
        self.client.login(username=self.invitee.username, password=PASSWORD)
        response = self.client.post(f"/invite_reject/{invite.id}/")
        self.assertFalse(
            Notification.objects.filter(recipient=self.invitee).unread().exists()
        )
        self.assertTrue(
            Notification.objects.filter(recipient=self.invitee).read().exists()
        )

    def test_gets_notification_on_event_edit(self):
        edited_event_form = self.example_form.copy()
        edited_event_form["title"] = "climbing"

        # invitee is an attendee to the event.
        # they should therefore get a notif if it is edited
        Event.objects.get(id=self.event_id).participants.add(self.invitee)

        response = self.client.post(f"/event/{self.event_id}/edit/", edited_event_form)
        
        notifications = Notification.objects.filter(recipient=self.invitee, verb="event edited")
        self.assertEqual(len(notifications), 1)
        self.assertTrue(notifications.exists())
        
        # the host who edited should not get notif
        notifications = Notification.objects.filter(recipient=self.inviter, verb="event edited")
        self.assertFalse(notifications.exists())

    def test_gets_notification_on_event_delete(self):
        # invitee is an attendee to the event.
        # they should therefore get a notif if it is deleted
        Event.objects.get(id=self.event_id).participants.add(self.invitee)

        response = self.client.post(f"/event/{self.event_id}/edit/delete/")
        
        notifications = Notification.objects.filter(recipient=self.invitee, verb="event deleted")
        self.assertEqual(len(notifications), 1)
        self.assertTrue(notifications.exists())

        # the host who deleted should not get notif
        notifications = Notification.objects.filter(recipient=self.inviter, verb="event deleted")
        self.assertFalse(notifications.exists())

    def test_gets_notification_on_participant_delete(self):
        # invitee is an attendee to the event.
        # they should therefore get a notif if it is deleted
        Event.objects.get(id=self.event_id).participants.add(self.invitee)

        response = self.client.post(f"/event/{self.event_id}/participant_delete/{self.invitee.id}/")
        
        notifications = Notification.objects.filter(recipient=self.invitee, verb="participant deleted")
        self.assertEqual(len(notifications), 1)
        self.assertTrue(notifications.exists())
