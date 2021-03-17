from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
from django.contrib.auth.models import User, UserManager
import datetime as dt
from django.http import JsonResponse

username='Ola'
email='ola@mail.com'
password='ola123'
class MyPageTest(TestCase):
    
    def setUp(self):
        user = User.objects.create_user(username, email, password)
        self.client.login(username=username, password=password)
    
    def test_valid_user(self):
        response = self.client.get("/mypage/")
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_user(self):
        self.client.logout()
        response = self.client.get("/mypage/")
        # Redirect to login if not logged in
        self.assertEqual(response.status_code, 302)
        self.client.login(username=username, password=password)