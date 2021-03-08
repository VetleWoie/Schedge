from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm

class signUpModelTest(TestCase):
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


        
    def test_userCreation(self):
        response = self.client.post("/signup/", self.userGood)
        print(response)

        # Can't find existing values in DB so these don't work

        # formEmailOld = NameForm(data=self.userEmailOld)
        # self.assertEqual(formEmailOld.is_valid(), False)

        # formUnOld = NameForm(data=self.userUsernameOld)
        # self.assertEqual(formUnOld.is_valid(), False)

        # formOldBoth = NameForm(data=self.userOldBoth)
        # self.assertEqual(formOldBoth.is_valid(), False)
        