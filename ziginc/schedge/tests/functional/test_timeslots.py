from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from unittest import skip

from schedge.forms import TimeSlotForm
from schedge.model_utils import create_time_slot

class TimeSlotFunctionalTest(TestCase):
    def setUp(self):
        self.example_event_model = {
            "title": "golfing",
            "location": "golf course",
            "description": ":)",
            "starttime": dt.time(00,00,00),
            "endtime": dt.time(00,00,00),
            "startdate": dt.datetime.now(),
            "enddate": dt.datetime.now() + dt.timedelta(days=7),
            "duration": dt.timedelta(hours=2),
        }

        self.testevent = Event.objects.create(**self.example_event_model)

        user = {
                "username" : "testUsername",
                "first_name" : "testFirstName",
                "last_name" : "testLastName",
                "email" : "testMail@riise.no",
                "password" : "testPassword",
        }
        self.user = User.objects.create_user(**user)
        self.testevent.participants.add(self.user)

        self.client.login(username=self.user.username, password=user["password"])
        self.tomorrow = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y-%m-%d")
        self.example_timeslot = {
            "date": self.tomorrow,
            "start_time": "09:10",
            "end_time" : "11:10",
        }
    
    def test_create_time_slot(self):
        expected = {
            "event": self.testevent,
            "start_time": dt.time(8,00,00),
            "end_time": dt.time(14,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date(),
            "creator": self.user,
        }

        t1 = {
            "start_time": dt.time(8,00,00),
            "end_time": dt.time(10,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date()
        }
        t2 = {
            "start_time": dt.time(12,00,00),
            "end_time": dt.time(14,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date()
        }
        t3 = {
            "start_time": dt.time(10,00,00),
            "end_time": dt.time(12,00,00),
            "date": (dt.datetime.now() + dt.timedelta(1)).date()
        }
        
        create_time_slot(self.testevent, self.user, t1)
        create_time_slot(self.testevent, self.user, t2)
        create_time_slot(self.testevent, self.user, t3)

        timeslots = TimeSlot.objects.all()
        self.assertEqual(len(timeslots), 1, msg="Should only be one timeslot, found %s" % len(timeslots))        
        timeslots = timeslots[0]
        #Check timeslot values
        self.assertEqual(timeslots.start_time,expected["start_time"] , msg="Start time should be %s but got %s" % (expected['start_time'], timeslots.start_time))        
        self.assertEqual(timeslots.end_time,expected["end_time"] , msg="End time should be %s but got %s" % (expected['end_time'], timeslots.end_time))
        self.assertEqual(timeslots.date,expected["date"] , msg="Date should be %s but got %s" % (expected['date'], timeslots.date))
        self.assertEqual(timeslots.creator,expected["creator"], msg="Creator should be %s but got %s" % (expected["creator"], timeslots.creator))    

    def test_rollover_time_slot(self):
        t1 = {
            "start_time": dt.time(23,00,00),
            "end_time": dt.time(1,00,00),
            "date": dt.datetime.now(),
        }
        
        form = TimeSlotForm(event=self.testevent,data=t1)
        #Check errors in start time
        with self.assertRaises(KeyError,msg="Expected no errors but got error(s) in starttime."):
            print("\nExpected no errors in start time but got %d \n Errors: \n %s" % (len(form.errors["start_time"]),form.errors["start_time"]))
            
        #Check errors in end time    
        with self.assertRaises(KeyError,msg="Expected no errors but got error(s) in end time."):
            print("\nExpected no errors in end time but got %d \n Errors: \n %s" % (len(form.errors["end_time"]),form.errors["end_time"]))
    
    def test_rollover_time_slot_with_invalid_length(self):
        t1 = {
            "start_time": dt.time(23,30,00),
            "end_time": dt.time(00,30,00),
            "date": dt.datetime.now(),
        }
        
        form = TimeSlotForm(event=self.testevent,data=t1)
        try:
            #Check errors in start time
            self.assertEqual(len(form.errors["start_time"]), 1, msg="Expected 1 error in start time got %d" % len(form.errors["start_time"]))            
            #Check errors in end time    
            self.assertEqual(len(form.errors["end_time"]), 1, msg="Expected 1 error in end_time got %d" % len(form.errors["end_time"]))    
        except Exception as e:
            self.fail("Got exeption: %s" % e)

    def test_create_timeslot(self):
        response = self.client.post(f"/event/{self.testevent.id}/", self.example_timeslot)
        # there is a timeslot in the context
        self.assertTrue(response.context["your_timeslots"])
        self.assertEqual(response.status_code, 200)

    def test_create_timeslot_in_the_past(self):
        timeslot = {
            "date": "1969-07-20",
            "start_time": "20:17",
            "end_time": "22:00"
            
        }
        response = self.client.post(f"/event/{self.testevent.id}/", timeslot)
        # there is a timeslot in the context
        self.assertEqual(response.status_code, 400)
    
    def test_delete_timeslot(self):
        create_time_slot(self.testevent, self.user, self.example_timeslot)
        events = Event.objects.all()
        timeslots = TimeSlot.objects.all()
        event_id = events[0].id
        timeslot_id = timeslots[0].id
        response = self.client.post('/event/%d/delete/%d/'%(event_id, timeslot_id))
        self.assertEqual(response.status_code, 302)
        timeslots = TimeSlot.objects.all()
        self.assertEqual(len(timeslots), 0)

    def test_delete_non_existing_timeslot_with_existing_event(self):
        create_time_slot(self.testevent, self.user, self.example_timeslot)
        events = Event.objects.all()
        event_id = events[0].id
        timeslot_id = 100
        response = self.client.post('/event/%d/delete/%d/'%(event_id, timeslot_id))
        self.assertEqual(response.status_code, 404)
        timeslots = TimeSlot.objects.all()
        self.assertEqual(len(timeslots), 1)
    
    def test_delete_timeslot_on_non_existing_event(self):
        create_time_slot(self.testevent, self.user, self.example_timeslot)
        event_id = 100
        timeslot_id = 1
        response = self.client.post('/event/%d/delete/%d/'%(event_id, timeslot_id))
        self.assertEqual(response.status_code, 404)
        timeslots = TimeSlot.objects.all()
        self.assertEqual(len(timeslots), 1)

    @skip("need better form validation on the timeslots")
    def test_create_timeslot_outside_range(self):
        # even't time interval is 8:30 am to 11:45 am
        # posting timeslot at 13:00 should fail
        timeslot = {
            "date": self.tomorrow,
            "start_time": "13:00",
            "end_time": "15:00",
        }
        response = self.client.post(f"/event/{self.testevent.id}/", timeslot)
        self.assertEqual(response.status_code, 400)

        # enddate is in one week. try posting timeslot in two weeks
        in_two_weeks = (dt.datetime.now() + dt.timedelta(days=14)).strftime("%Y-%m-%d")
        timeslot = {
            "date": in_two_weeks,
            "start_time": "09:10",
            "end_time": "13:00",
        }
        response = self.client.post(f"/event/{self.testevent.id}/", timeslot)
        self.assertEqual(response.status_code, 400)
