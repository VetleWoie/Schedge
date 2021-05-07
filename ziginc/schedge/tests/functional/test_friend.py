from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test.utils import freeze_time
from schedge.models import FriendRequest
from unittest import skip


class FriendFunctionalTest(TestCase):
    def setUp(self):
        #Set up three test users to test friend functionality
        self.users = []
        #create ten test users
        self.password = "testPassword"
        for i in range(4):
            user = {
                "username" : "testUsername_%d" %i,
                "first_name" : "testFirstName_%d"%i,
                "last_name" : "testLastName_%d"%i,
                "email" : "testMail_%d@riise.no"%i,
                "password" : self.password,
            }
            self.users.append(User.objects.create_user(**user))
        #Create friend request between user 0 and 1 
        form = {'to_user': self.users[1].username}
        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_invite_send/', form)
        self.assertEqual(response.status_code, 200, msg = "Expected status code 200 got %d"%response.status_code)
        self.client.logout()
        #Create friend request between user 0 and 1 
        form = {'to_user': self.users[2].username}
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.post(f'/friend_invite_send/', form)
        self.assertEqual(response.status_code, 200, msg = "Expected status code 200 got %d"%response.status_code)
        #Make user 1 and 3 friends
        self.users[0].profile.friends.add(self.users[3])
        self.users[3].profile.friends.add(self.users[0])
        
    def test_send_friend_request_to_valid_user(self):
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 2, msg = "Expected 1 friend request got %d"%len(friend_requests))
        self.assertEqual(friend_requests[0].from_user, self.users[0])
        self.assertEqual(friend_requests[0].to_user, self.users[1])
        
    def test_send_friend_request_to_non_existing_user(self):
        form = {'to_user': "Gibberish"}
        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_invite_send/', form)
        self.assertEqual(response.status_code, 404, msg = "Expected status code 404 got %d"%response.status_code)
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests),2)

    def test_accept_existing_friend_request(self):
        #Respond to friend request
        friend_requests = FriendRequest.objects.all()
        self.client.logout()
        self.client.login(username=self.users[1].username, password=self.password)

        response = self.client.post(f'/friend_invite_accept/{friend_requests[0].id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(friend_requests), 1)
        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 2)
        self.assertEqual(friends[0], self.users[1])

    def test_reject_existing_friend_request(self):
        friend_requests = FriendRequest.objects.all()
        self.client.logout()
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.post(f'/friend_invite_reject/{friend_requests[0].id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(friend_requests), 1)

        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 1)

    def test_accept_non_existing_friend_request(self):
        #Respond to friend request
        friend_requests = FriendRequest.objects.all()
        self.client.logout()
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.post(f'/friend_invite_accept/2000/')
        self.assertEqual(response.status_code, 404)

    def test_reject_non_existing_friend_request(self):
        #Respond to friend request
        friend_requests = FriendRequest.objects.all()
        self.client.logout()
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.post(f'/friend_invite_reject/2000/')
        self.assertEqual(response.status_code, 404)

    def test_accept_others_friend_request(self):
        #Respond to friend request
        friend_requests = FriendRequest.objects.all()
        self.client.login(username=self.users[0].username, password=self.password)

        response = self.client.post(f'/friend_invite_accept/{friend_requests[1].id}/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(friend_requests), 2)
        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 1)

    def test_reject_others_friend_request(self):
        #Respond to friend request
        friend_requests = FriendRequest.objects.all()
        self.client.login(username=self.users[0].username, password=self.password)

        response = self.client.post(f'/friend_invite_reject/{friend_requests[1].id}/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(friend_requests), 2)
        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 1)
    
    def test_delete_existing_friend_request(self):
        form = {'to_user': self.users[1].username}
        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_invite_delete/', form)
        self.assertEqual(response.status_code, 200)

        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 1)

        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 1)

    def test_delete_non_existing_friend_request(self):
        #Respond to friend request
        form = {'to_user': 'Gibberish'}
        self.client.login(username=self.users[1].username, password=self.password)
        response = self.client.post(f'/friend_invite_delete/', form)
        self.assertEqual(response.status_code, 404)
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 2)

    def test_delete_others_friend_request(self):
        form = {'to_user': self.users[2].username}
        #Respond to friend request
        login = self.client.login(username=self.users[0].username, password=self.password)
        self.assertTrue(login)

        response = self.client.post(f'/friend_invite_delete/', form)
        self.assertEqual(response.status_code, 404)
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 2)

    def test_add_self_friend(self):
        form = {'to_user': self.users[0].username}
        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_invite_send/', form)
        self.assertEqual(response.status_code, 400, msg = "Expected status code 400 got %d"%response.status_code)
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests),2)
    
    def test_delete_user_with_pending_outgoing_friend_request(self):
        self.users[0].delete()
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 1)
    
    def test_delete_user_with_pending_incoming_friend_request(self):
        self.users[1].delete()
        friend_requests = FriendRequest.objects.all()
        self.assertEqual(len(friend_requests), 0)

    def test_delete_user_with_friend(self):
        #Respond to friend request
        self.client.logout()
        self.users[3].delete()
        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends),0)
    
    def test_delete_existing_friend(self):
        form = {'to_user': self.users[3].username}

        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_delete/', form)
        self.assertEqual(response.status_code, 200)

        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 0)
    
    def test_delete_non_existing_friend(self):
        form = {'to_user': 'Gibberish'}

        self.client.login(username=self.users[0].username, password=self.password)
        response = self.client.post(f'/friend_delete/', form)
        self.assertEqual(response.status_code, 404)

        friends = self.users[0].profile.friends.all()
        self.assertEqual(len(friends), 1)