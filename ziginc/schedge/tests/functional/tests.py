from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event
import datetime

class EventModelTest(TestCase):
    def test_create_events(self):
        starttime = datetime.time(10, 30, 0)
        startdate = datetime.date(2028,4,8)
        # Event.objects.create(title='one event', startDate)