"""
Tests for models.py
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test for new user email normalize"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@Example.com', 'TEST3@example.com'],
            ['TEST4@EXAMPLE.com', 'TEST4@example.com'],
            ['Test5@example.COM', 'Test5@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='sample123',
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """When user doesn't provide email rasie a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """test to create a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
