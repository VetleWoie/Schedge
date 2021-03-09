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


class CreateEventSeleniumTest(StaticLiveServerTestCase):
    """Functional test of the create event page using Selenium"""

    def setUp(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(firefox_options=options)

        # create user and login
        user = User.objects.create_user("tester", "myemail@test.com", "Elias123")
        self.client.login(username="tester", password="Elias123")

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

    def input_date(self, id_, date):
        datefield = self.driver.find_element_by_id(id_)
        # start chain
        chain = ActionChains(self.driver)
        # move to field and click
        chain.move_to_element(datefield).click()
        # send date input
        chain.send_keys(date)
        # perform the actions
        chain.perform()

    def input_time(self, id_, time):
        timefield = self.driver.find_element_by_id(id_)
        chain = ActionChains(self.driver)
        # move and click
        chain.move_to_element(timefield).click()
        # press shift+tab to move back to hour position
        # a click moves cursor to minute position
        chain.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT)
        # send time input
        chain.send_keys(time)
        chain.perform()

    def test_selenium(self):
        # move to create event page
        self.driver.get(self.live_server_url + "/createevent/")

        # start filling in the fields

        title_field = self.driver.find_element_by_id("id_title")
        title_field.send_keys("Test Event")

        location_field = self.driver.find_element_by_id("loc")
        location_field.send_keys("Test Location")

        self.input_time("id_starttime", "0800AM")
        self.input_time("id_endtime", "0430PM")

        self.input_date("id_startdate", "01012022")
        self.input_date("id_enddate", "01012023")

        # submit form
        submit_btn = self.driver.find_element_by_id("id_submit_btn")
        submit_btn.click()

        # wait for new site to load
        sleep(0.5)

        # url ends with /event/[some number]/
        self.assertRegex(self.driver.current_url, "^.*\/event\/\d+\/$")

        # assert the site we land at has the same title
        title = self.driver.find_element_by_id("id_event_title").text
        self.assertEqual(title, "Test Event")

    def tearDown(self):
        self.driver.quit()