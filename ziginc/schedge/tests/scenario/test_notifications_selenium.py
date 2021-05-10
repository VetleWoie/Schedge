from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from notifications.models import Notification

PASSWORD = "Elias123"


class NotificationsSeleniumTest(StaticLiveServerTestCase):
    """Functional test of the create event page using Selenium"""

    def setUp(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")

        self.driver = webdriver.Firefox(firefox_options=options)
        # create user and login
        self.host = User.objects.create_user(
            "host", "host@test.com", PASSWORD, first_name="Host", last_name="McHost"
        )
        self.guest = User.objects.create_user(
            "guest",
            "guest@test.com",
            PASSWORD,
            first_name="Guest",
            last_name="McGuest",
        )

        self.client.login(username=self.host.username, password=PASSWORD)

        # get session cookie
        cookie = self.client.cookies["sessionid"]
        # go to home page
        self.driver.get(self.live_server_url)
        # add the client's session cookie. this logs us in in the browser
        self.driver.add_cookie(
            {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
        )
        # refresh to make the cookie take effect
        self.driver.refresh()

        self.tomorrow = dt.date.today() + dt.timedelta(days=1)
        self.next_week = dt.date.today() + dt.timedelta(days=7)
        self.event = Event.objects.create(
            title="hiking",
            location="kilimanjaro",
            description="remember to bring shoes",
            starttime=dt.time(13, 0),
            endtime=dt.time(23, 0),
            startdate=self.tomorrow,
            enddate=self.next_week,
            duration=dt.timedelta(hours=6),
            status="U",
            host=self.host,
        )
        self.event.participants.add(self.host)

    def login(self, username):
        self.client.logout()
        self.client.login(username=username, password=PASSWORD)
        cookie = self.client.cookies["sessionid"]
        # add the client's session cookie. this logs us in in the browser
        self.driver.add_cookie(
            {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
        )

    def test_notif_on_invite(self):
        self.driver.get(self.live_server_url + f"/event/{self.event.id}")
        sleep(1.5)
        
        invite_form = self.driver.find_element_by_id("id_invitee")
        invite_form.send_keys("guest")
        invite_submit = self.driver.find_element_by_id("invite-submit")
        invite_submit.click()
        sleep(0.8)

        self.login(self.guest.username)
        # sleep(0.4)
        self.driver.get(self.live_server_url + f"/mypage/")
        sleep(1.5)

        self.assertTrue(Notification.objects.filter(recipient=self.guest).exists())

        invite_accept_btn = self.driver.find_element_by_id("id_notif_invite_accept")

        # press accept button. we must do it this way as the button is hidden
        self.driver.execute_script("$(arguments[0]).click();", invite_accept_btn)

        sleep(0.8)
        guestparticipant = self.event.participants.get(id=self.guest.id)
        self.assertTrue(guestparticipant)
        notifs = Notification.objects.filter(recipient=self.host)
        self.assertEqual(notifs.count(), 1)
        notif = notifs[0]
        self.assertEqual(notif.actor, self.guest)
        self.assertEqual(notif.data["title"], "hiking")

    def tearDown(self):
        self.driver.quit()
