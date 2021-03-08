from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse, response

class MypageTest(TestCase):
    def test_invalid_user(self):
        response = self.client.get("/mypage")
        self.assertEqual(response.url, "/mypage")