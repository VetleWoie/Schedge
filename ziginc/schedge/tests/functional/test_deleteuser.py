from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from schedge.forms import NameForm

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

    def test_deleteuser(self):
        response = self.client.post("/signup/", self.userGood)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.userGood["username"], password=self.userGood["password"])

        response2 = self.client.post("/mypage/delete_user_account/")
        self.assertEqual(response2.url, "/signup/")