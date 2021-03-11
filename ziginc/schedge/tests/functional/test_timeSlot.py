from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User, UserManager
import datetime as dt
from django.http import JsonResponse


class TimeSlotTest(TestCase):
    def setUp(self):
        user_1 = {
            "username" : "elias",
            "first_name" : "Elias",
            "last_name" : "Riiser",
            "email" : "elias@riise.no",
            "password" : "Elias123",
        }
        user_2 = {
            "username" : "vetle",
            "first_name" : "Vetle",
            "last_name" : "Woie",
            "email" : "vetle@woie.no",
            "password" : "Elias123"
        }
        self.user_1 = User.objects.create_user(**user_1)
        self.user_2 = User.objects.create_user(**user_2)
        # self.client.login(username="elias", password="Elias123")

        e = {
            "title" : "testevent",
            "startdate" : dt.date(2020,1,1),
            "enddate" : dt.date(2020,1,2),
            "starttime" : dt.time(00,00,00),
            "endtime" : dt.time(00,00,00),
            "duration" : dt.timedelta(hours=2),
        }
        self.e = Event.objects.create(**e, host=User.objects.get(username="elias"))
    
    def test_same_time_slot(self):
        print()
        t1 = TimeSlot.objects.create(starttime = dt.time(12,00,00),
                                    endtime = dt.time(16,00,00),
                                    date= dt.date(2020,1,1),
                                    event = self.e,
                                    creator = self.user_1)

        t2 = TimeSlot.objects.create(starttime = dt.time(12,00,00),
                                    endtime = dt.time(16,00,00),
                                    date= dt.date(2020,1,1),
                                    event = self.e,
                                    creator = self.user_2)

        self.e.findTimeSlot()
        




        