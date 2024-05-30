"""
Tests for user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserAPI(TestCase):
    """Test for public features of user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Tests for creating user is sucessful"""
        payload = {
            'email' : 'test@example.com',
            'password' : 'testpass123',
            'name' : 'test_name',
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exixts(self):
        """Test error returned if user exists"""
        payload = {
            'email' : 'test@example.com',
            'password' : 'testpass123',
            'name' : 'test_name',
        }
        create_user(payload)
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passeord_too_short_error(self):
        """Test returns error if Passeord is too short < 5 chars"""

        payload = {
            'email' : 'test@example.com',
            'password' : 'test',
            'name' : 'test_name',
        }

        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exixts = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertEqual(user_exixts)