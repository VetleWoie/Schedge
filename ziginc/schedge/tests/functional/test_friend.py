from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import datetime as dt
from django.http import JsonResponse
from unittest import skip


class TimeSlotFunctionalTest(TestCase):
    def setUp(self):
        #Set up three test users to test friend functionality
        self.users = []
        #create ten test users
        for i in range(3):
            user = {
                "username" : "testUsername_%d" %i,
                "first_name" : "testFirstName_%d"%i,
                "last_name" : "testLastName_%d"%i,
                "email" : "testMail_%d@riise.no"%i,
                "password" : "testPassword_%d"%i,
            }
            self.users.append(User.objects.create_user(**user))
    
    def test_send_friend_request_to_valid_user(self):
        pass        
    def test_send_friend_request_to_non_valid_user(self):
        pass
    def test_accept_existing_friend_request(self):
        pass
    def test_reject_existing_friend_request(self):
        pass
    def test_accept_non_existing_friend_request(self):
        pass
    def test_reject_non_existing_friend_request(self):
        pass
    def test_accept_others_friend_request(self):
        pass
    def test_reject_others_friend_request(self):
        pass