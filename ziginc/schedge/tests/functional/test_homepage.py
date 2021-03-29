from django.test import TestCase
from django.core.exceptions import ValidationError
from schedge.models import Event, TimeSlot
from schedge.forms import EventForm
import datetime as dt
from django.http import JsonResponse
from django.contrib.auth.models import User
from random import randrange


class HomepageTest(TestCase):
    def test_0_users(self):
        response = self.client.get("/")
        self.assertEqual(response.context["user_count"], 0) 

    def test_1_user(self):
        User.objects.create_user("Alice", "alice@test.com", "Elias123")
        response = self.client.get("/")
        self.assertEqual(response.context["user_count"], 1)
        self.assertIn(b"person", response.content)

    def test_2_users(self):
        User.objects.create_user("Alice", "alice@test.com", "Elias123")
        User.objects.create_user("Bob", "bob@test.com", "Elias123")

        response = self.client.get("/")
        self.assertEqual(response.context["user_count"], 2)
        self.assertIn(b"people", response.content)

    def test_n_users(self):
        n = randrange(10, 100)
        for i in range(n):
            User.objects.create_user(f"User{i}", f"user{i}@test.com", "Elias123")

        response = self.client.get("/")
        self.assertEqual(response.context["user_count"], n)
