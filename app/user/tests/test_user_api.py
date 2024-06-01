"""
Tests for user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'test_name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exixts(self):
        """Test error returned if user exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'test_name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test returns error if Passeord is too short < 5 chars"""

        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'test_name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exixts = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exixts)

    def test_create_token_for_user(self):
        """Generates token for valid credentials."""
        user_details = {
            "name": 'test_name',
            "email": 'testmail@example.com',
            "password": 'testpassword'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_toke_bad_credentials(self):
        '''Test returns error when credentials are invalid'''

        create_user(email='test@example.com', password='testpassword')
        payload = {
            'email': 'test@example.com',
            'password': 'badpassword'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Returns a error when creating a blank password"""

        create_user(email='test@example.com', password='testpassword')
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        '''Test authentication is required for user'''
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    '''API tests required for authentication'''
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpassword123',
            name='testuser'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retive_profile_success(self):
        '''Test retriving profile for logged in user'''
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        '''Test POST is not allowed for this endpoint'''
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        '''Test Update profile for authenticated user'''

        payload = {
            'name': 'updated name',
            'password': 'NewPassword@123',
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
