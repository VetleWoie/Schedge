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
        chain.move_to_element(timefield)
        chain.click()

        # send time input
        chain.send_keys(time)
        chain.perform()

    def test_selenium(self):
        # move to create event page
        self.driver.get(self.live_server_url + "/createevent/")

        # start filling in the fields

        title_field = self.driver.find_element_by_id("id_title")
        title_field.send_keys("Test Event")

        nextbtn = self.driver.find_element_by_id("next1")
        nextbtn.click()

        location_field = self.driver.find_element_by_id("id_location")
        location_field.send_keys("Test Location")

        # sleep(2)

        nextbtn = self.driver.find_element_by_id("next2")
        nextbtn.click()

        self.input_date("id_startdate", "01-01-2022")
        self.input_date("id_enddate", "01-01-2023")

        nextbtn = self.driver.find_element_by_id("next3")
        nextbtn.click()

        # find all three duration forms
        duration_inputs = self.driver.find_elements_by_class_name("duration-form")
        for field, num in zip(duration_inputs, [1, 0]):
            field.send_keys(str(num))
        # location_field.send_keys("Test Location")

        nextbtn = self.driver.find_element_by_id("next4")
        nextbtn.click()

        self.input_time("id_starttime", "0800PM")
        self.input_time("id_endtime", "1630AM")
        
        nextbtn = self.driver.find_element_by_id("next5")
        nextbtn.click()

        # submit form
        submit_btn = self.driver.find_element_by_id("event_url")
        submit_btn.click()
    
        # wait for new site to load
        sleep(1)

        # url ends with /event/[some number]/
        self.assertRegex(self.driver.current_url, "^.*\/event\/\d+\/$")

        # assert the site we land at has the same title
        title = self.driver.find_element_by_id("id_event_title").text
        self.assertEqual(title, "Test Event")

    def tearDown(self):
        self.driver.quit()