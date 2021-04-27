from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User, UserManager
import datetime as dt
from django.http import JsonResponse


class MyPageTest(TestCase):
    
    def setUp(self):
        self.me = User.objects.create_user('Ola', 'ola@mail.com', 'Elias123')
        self.client.login(username=self.me.username, password='Elias123')
        
        # Insert events spanning more than one week forward in time.
        for i in range(5):
            self.example_model = {
                "title": f"Studying{i}",
                "location": "UiT",
                "description": f"Studying really hard to get good grades. {i}",
                "starttime": dt.time(),
                "endtime": dt.time(hour=4),
                "startdate": dt.datetime.now() + dt.timedelta(days=2*i),
                "enddate": dt.datetime.now() + dt.timedelta(days=1 + 3*i),
                "duration": dt.timedelta(hours=2),
                "status":"C"
            }
            Event.objects.create(**self.example_model)
    
    def test_valid_user(self):
        response = self.client.get("/mypage/")
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_user(self):
        self.client.logout()
        response = self.client.get("/mypage/")
        # Redirect to login if not logged in
        self.assertEqual(response.status_code, 302)
        self.client.login(username=self.me.username, password='Elias123')

    
    def test_this_weeks_events(self):
        # TODO: Change this out for somehitng that checks the webpage and not just the logic for how to find these events.
        # Might want to add more thourough test as well. With logged in user etc.
        today = dt.date.today()
        in_seven_days = today + dt.timedelta(days=7)
        this_weeks_events = Event.objects.filter(status="C", startdate__gte=today, enddate__lte=in_seven_days).count()
        self.assertEqual(this_weeks_events, 3)
         
