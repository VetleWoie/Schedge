from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm

class SignUpModelTest(TestCase):
    def setUp(self):
        # self.goodUser = request.post

        self.userPWBad = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias",
        }
        self.userEmailBad = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "testing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }
        self.userBadBoth = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "testing.com",
            "password" : "Elias123",
            "password2" : "Elias",
        }
        self.userGood = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }
        self.userUsernameOld = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ingg.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }
        self.userEmailOld = {
            "username" : "test2",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }
        self.userOldBoth = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }

    def test_fields(self):
        formPWbad = NameForm(data=self.userPWBad)
        self.assertEqual(formPWbad.is_valid(), False)
        
        formEmailBad = NameForm(data=self.userEmailBad)
        self.assertEqual(formEmailBad.is_valid(), False)
        
        formBadBoth = NameForm(data=self.userBadBoth)
        self.assertEqual(formBadBoth.is_valid(), False)
        
        formGood = NameForm(data=self.userGood)
        self.assertEqual(formGood.is_valid(), True)


        
    def test_user_creation(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        # Can't find existing values in DB so these don't work

        response = self.client.post("/signup/", self.userEmailOld)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/signup/", self.userUsernameOld)
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/signup/", self.userOldBoth)
        self.assertEqual(response.status_code, 200)
        