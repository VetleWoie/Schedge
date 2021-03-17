from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot, PotentialTimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User, UserManager
import datetime as dt
from django.http import JsonResponse

from schedge.utils import riise_hofsøy


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
            riise_hofsøy(self.event)

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
        riise_hofsøy(self.event)

        t2 = TimeSlot.objects.create(start_time = dt.time(12,00,00),
                                    end_time = dt.time(18,00,00),
                                    date= dt.date(2020,1,1),
                                    event = self.event,
                                    creator = self.users[1])
        riise_hofsøy(self.event)
        
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
    
    def test_multiple_overlapping_time_slots(self):
        e = {
            "title" : "testevent",
            "startdate" : dt.date(2020,1,1),
            "enddate" : dt.date(2020,1,2),
            "starttime" : dt.time(00,00,00),
            "endtime" : dt.time(00,00,00),
            "duration" : dt.timedelta(hours=1),
        }
        event = Event.objects.create(**e, host=self.users[0])

        expected = [
            {
            "event" : event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(13,00,00),
            "date" : dt.date(2020,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : event,
            "start_time" : dt.time(12,30,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2020,1,1),
            "users" : [self.users[0], self.users[2]],
            },
            {
            "event" : event,
            "start_time" : dt.time(14,00,00),
            "end_time" : dt.time(15,00,00),
            "date" : dt.date(2020,1,1),
            "users" : [self.users[0], self.users[2], self.users[3]],
            },
            {
            "event" : event,
            "start_time" : dt.time(16,00,00),
            "end_time" : dt.time(17,00,00),
            "date" : dt.date(2020,1,1),
            "users" : [self.users[2], self.users[4]],
            },
        ]

        t0 = TimeSlot.objects.create(start_time = dt.time(10,00,00),
                                    end_time = dt.time(16,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[0])
        riise_hofsøy(event)

        t1 = TimeSlot.objects.create(start_time = dt.time(11,00,00),
                                    end_time = dt.time(13,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[1])
        riise_hofsøy(event)

        t2 = TimeSlot.objects.create(start_time = dt.time(12,30,00),
                                    end_time = dt.time(18,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[2])
        riise_hofsøy(event)

        t3 = TimeSlot.objects.create(start_time = dt.time(14,00,00),
                                    end_time = dt.time(15,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[3])
        riise_hofsøy(event)

        t4 = TimeSlot.objects.create(start_time = dt.time(16,00,00),
                                    end_time = dt.time(17,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[4])
        riise_hofsøy(event)

        t5 = TimeSlot.objects.create(start_time = dt.time(17,30,00),
                                    end_time = dt.time(18,30,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[5])
        riise_hofsøy(event)

        t6 = TimeSlot.objects.create(start_time = dt.time(20,00,00),
                                    end_time = dt.time(21,00,00),
                                    date= dt.date(2020,1,1),
                                    event = event,
                                    creator = self.users[6])
        riise_hofsøy(event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")

        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        

        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

    def test_same_time_diffrent_date(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(10,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(10,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,2),
            "users" : [self.users[2], self.users[3]],
            },
        ]
        
        date = dt.date(2021,1,1)
        for user in self.users:
            if user == self.users[4]:
                break
            elif user == self.users[2]:
                date = dt.date(2021,1,2)
            TimeSlot.objects.create(start_time = dt.time(10,00,00),
                                    end_time = dt.time(16,00,00),
                                    date = date,
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("date")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

    def test_nested_time_slot_same_date_with_valid_length_overlap_and_first_in_last_out(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(17,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(15,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(13,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1], self.users[0]],
            },
        ]

        for i,user in enumerate(self.users):
            if user == self.users[4]:
                break
            TimeSlot.objects.create(start_time = dt.time(11-2*i,00,00),
                                    end_time = dt.time(13+2*i,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)
    
    def test_nested_time_slot_same_date_with_valid_length_overlap_and_first_in_first_out(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1],self.users[0]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(18,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2]],
            },
        ]

        for i,user in enumerate(self.users):
            if user == self.users[4]:
                break
            TimeSlot.objects.create(start_time = dt.time(5+2*i,00,00),
                                    end_time = dt.time(14+2*i,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

    def test_nested_time_slot_same_date_with_non_valid_length_overlap_and_first_in_last_out(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(3,00,00),
            "end_time" : dt.time(21,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(4,00,00),
            "end_time" : dt.time(20,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(5,00,00),
            "end_time" : dt.time(19,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(6,00,00),
            "end_time" : dt.time(18,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],self.users[5],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(17,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],self.users[5],self.users[4],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(8,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],self.users[5],self.users[4],self.users[3],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(15,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],self.users[5],self.users[4],self.users[3],self.users[2],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(10,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[9],self.users[8],self.users[7],self.users[6],self.users[5],self.users[4],self.users[3],self.users[2],self.users[1],],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(13,00,00),
            "date" : dt.date(2021,1,1),
            "users" : self.users,
            },
        ]

        for i,user in enumerate(self.users):
            TimeSlot.objects.create(start_time = dt.time(11-i,00,00),
                                    end_time = dt.time(13+i,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

def test_nested_time_slot_same_date_with_non_valid_length_overlap_and_first_in_first_out(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(15,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1],self.users[0]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(15,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(16,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[3], self.users[2]],
            },
        ]

        for i,user in enumerate(self.users):
            if user == self.users[4]:
                break
            TimeSlot.objects.create(start_time = dt.time(5+2*i,00,00),
                                    end_time = dt.time(14+i,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

def test_nested_time_slot_same_date_with_valid_length_overlap_and_same_end(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2], self.users[3]],
            },
        ]

        for i,user in enumerate(self.users):
            if user == self.users[4]:
                break
            TimeSlot.objects.create(start_time = dt.time(5+2*i,00,00),
                                    end_time = dt.time(14,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)
        
        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)

def test_nested_time_slot_same_date_with_valid_length_overlap_and_same_end_and_one_premature_end(self):
        expected = [
            {
            "event" : self.event,
            "start_time" : dt.time(7,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(9,00,00),
            "end_time" : dt.time(14,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2]],
            },
            {
            "event" : self.event,
            "start_time" : dt.time(11,00,00),
            "end_time" : dt.time(13,00,00),
            "date" : dt.date(2021,1,1),
            "users" : [self.users[0], self.users[1], self.users[2], self.users[3]],
            },
        ]

        for i,user in enumerate(self.users):
            if user == self.users[3]:
                break
            TimeSlot.objects.create(start_time = dt.time(5+2*i,00,00),
                                    end_time = dt.time(14,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = user)
            riise_hofsøy(self.event)

        TimeSlot.objects.create(start_time = dt.time(11,00,00),
                                    end_time = dt.time(13,00,00),
                                    date = dt.date(2021,1,1),
                                    event = self.event,
                                    creator = self.users[3])
        riise_hofsøy(self.event)

        #Get all potential timeslots from database
        potTimeSlot = PotentialTimeSlot.objects.order_by("start_time")


        #Check that it is four potential timeslots in the database
        self.assertEqual(len(potTimeSlot), len(expected), msg="Should be %s potential timeslots, found %s" % (len(expected),len(potTimeSlot)))        
        for i,time in enumerate(potTimeSlot):
            #Check timeslot values
            self.assertEqual(time.start_time,expected[i]["start_time"] , msg="Start time should be %s but got %s" % (expected[i]['start_time'], time.start_time))        
            self.assertEqual(time.end_time,expected[i]["end_time"] , msg="End time should be %s but got %s" % (expected[i]['end_time'], time.end_time))
            self.assertEqual(time.date,expected[i]["date"] , msg="Date should be %s but got %s" % (expected[i]['date'], time.date))
            #Check users
            users = time.participants.all()
            self.assertEqual(len(users), len(expected[i]["users"]), msg="Should be %s users in the timeslot got %s" % (len(expected[i]["users"]),len(users)))
            for user in expected[i]["users"]:
                self.assertIn(user, users)