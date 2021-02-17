from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse

class CourseModelTest(TestCase):
    def setUp(self):
        self.golf = Event.objects.create(
            title="golfing",
            location="golf course",
            description=":)",
            starttime=dt.time(),
            endtime=dt.time(hour=2),
            startdate=dt.datetime.now(),
            enddate=dt.datetime.now() + dt.timedelta(days=1),
            duration=dt.timedelta(hours=2),
        )
    
    def test_invalid_duration_field(self):

        with self.assertRaises(AttributeError):
            golf2 = Event.objects.create(
                title="golfing",
                location="golf course",
                description=":)",
                starttime=dt.time(),
                endtime=dt.time(),
                startdate=dt.datetime.now(),
                enddate=dt.datetime.now() + dt.timedelta(days=1),
                duration="string",
            )
            