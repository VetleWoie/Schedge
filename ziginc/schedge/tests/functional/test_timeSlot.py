from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, PotentialTimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User, UserManager
import datetime as dt
from django.http import JsonResponse

from schedge.views import find_potential_time_slots


class TimeSlotTest(TestCase):
    def setUp(self):

        self.users = []
        #create ten test users
        for i in range(10):
            user = {
                "username" : "testUsername_%d" %i,
                "first_name" : "testFirstName_%d"%i,
                "last_name" : "testLastName_%d"%i,
                "email" : "testMail_%d@riise.no"%i,
                "password" : "testPassword_%d"%i,
            }
            self.users.append(User.objects.create_user(**user))

        e = {
            "title" : "testevent",
            "startdate" : dt.date(2020,1,1),
            "enddate" : dt.date(2020,1,2),
            "starttime" : dt.time(00,00,00),
            "endtime" : dt.time(00,00,00),
            "duration" : dt.timedelta(hours=2),
        }
        self.event = Event.objects.create(**e, host=self.users[0])
        
    
    def test_same_time_slot(self):
        expected = {
            "event" : self.event,
            "start_time" : dt.time(12,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2020,1,1),
        }
        for user in self.users:
            t = TimeSlot.objects.create(start_time = dt.time(12,00,00),
                                        end_time = dt.time(16,00,00),
                                        date= dt.date(2020,1,1),
                                        event = self.event,
                                        creator = user)
            find_potential_time_slots(self.event, t)

        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.all()

        #Check that it is only one potential timeslot in the database
        self.assertEqual(len(potTimeSlot), 1, msg="Should only be one potential timeslot found %s" % len(potTimeSlot))        
        potTimeSlot = potTimeSlot[0]
        #Check timeslot values
        self.assertEqual(potTimeSlot.start_time,expected["start_time"] , msg="Start time should be %s but got %s" % (expected['start_time'], potTimeSlot.start_time))        
        self.assertEqual(potTimeSlot.end_time,expected["end_time"] , msg="End time should be %s but got %s" % (expected['end_time'], potTimeSlot.end_time))
        self.assertEqual(potTimeSlot.date,expected["date"] , msg="Date should be %s but got %s" % (expected['date'], potTimeSlot.date))
        #Check users
        users = potTimeSlot.participants.all()
        self.assertEqual(len(users), len(self.users), msg="Should be %s users in the timeslot got %s" % (len(self.users),len(users)))
        for user in self.users:
            self.assertIn(user, users)

    def test_diffrent_time_slot(self):
        expected = {
            "event" : self.event,
            "start_time" : dt.time(12,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2020,1,1),
        }
        t1 = TimeSlot.objects.create(start_time = dt.time(10,00,00),
                                    end_time = dt.time(16,00,00),
                                    date= dt.date(2020,1,1),
                                    event = self.event,
                                    creator = self.users[0])
        find_potential_time_slots(self.event, t1)

        t2 = TimeSlot.objects.create(start_time = dt.time(12,00,00),
                                    end_time = dt.time(18,00,00),
                                    date= dt.date(2020,1,1),
                                    event = self.event,
                                    creator = self.users[1])
        find_potential_time_slots(self.event, t2)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.all()

        #Check that it is only one potential timeslot in the database
        self.assertEqual(len(potTimeSlot), 1, msg="Should only be one potential timeslot found %s" % len(potTimeSlot))        
        potTimeSlot = potTimeSlot[0]
        #Check timeslot values
        self.assertEqual(potTimeSlot.start_time,expected["start_time"] , msg="Start time should be %s but got %s" % (expected['start_time'], potTimeSlot.start_time))        
        self.assertEqual(potTimeSlot.end_time,expected["end_time"] , msg="End time should be %s but got %s" % (expected['end_time'], potTimeSlot.end_time))
        self.assertEqual(potTimeSlot.date,expected["date"] , msg="Date should be %s but got %s" % (expected['date'], potTimeSlot.date))
        #Check users
        users = potTimeSlot.participants.all()
        self.assertEqual(len(users), 2, msg="Should be 2 users in the timeslot got %s" % len(users))
        self.assertIn(self.users[1], users)
        self.assertIn(self.users[0], users)

    def test_delete_event(self):
        expected = {
            "event" : self.event,
            "start_time" : dt.time(12,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2020,1,1),
        }

        pt = PotentialTimeSlot.objects.create(**expected)
        pt.participants.add(self.users[1])
        pt.participants.add(self.users[0])

        self.event.delete()

        events = Event.objects.all()

        #Check that event database is zero 
        self.assertEqual(len(events), 0, msg="Event table should be empty but found %s entries" % len(events))
        
        #Check that potential timeslot also is deleted
        potTimeSlots = PotentialTimeSlot.objects.all()
        self.assertEqual(len(potTimeSlots), 0, msg="Potential time slot database should be empty but found %s entries" % len(potTimeSlots))
        

        





        