from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm
from unittest import skip

class DeleteUserTest(TestCase):
    def setUp(self):
        # self.goodUser = request.post
        self.userGood = {
            "username" : "test",
            "first_name" : "Test",
            "last_name" : "ing",
            "email" : "test@ing.com",
            "password" : "Elias123",
            "password2" : "Elias123",
        }

    def test_deluser(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        self.client.post("/mypage/delete_user_account/")

        # Check that user does not exists after deletion.
        usr_exists = User.objects.filter(username=self.userGood["username"]).exists()
        self.assertEqual(usr_exists, False)

    @skip("Need the home view which is not present in this version of master, but which is implemented in another branch.")
    def test_deluser_redirect(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        response2 = self.client.post("/mypage/delete_user_account/")
        self.assertEqual(response2.url, "/home/")