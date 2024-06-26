"""
Tests for models.py
"""
from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


def create_user(email='test@example.com', password='testpassword123'):
    """Create and return a NewUser instance"""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipie(self):
        '''Test creating a recipie is successful'''
        user = get_user_model().objects.create_user(
            'testemial@gmail.com',
            'testpassword123'
        )

        recipie = models.Recipie.objects.create(
            user=user,
            title='sample title',
            time_minutes=5,
            price=Decimal('50.0'),
            description='sample recipie description',
        )

        self.assertEqual(str(recipie), recipie.title)

    def test_create_tag(self):
        """Test Create a tag"""
        user = create_user()

        tag = models.Tag.objects.create(
            user=user,
            name='testTag'
        )

        self.assertEqual(tag.name, str(tag))

    def test_create_ingredient(self):
        """Test Create an ingredient"""
        user = create_user()

        ingredient = models.Ingredient.objects.create(
            user=user,
            name='testIngredient'
        )

        self.assertEqual(ingredient.name, str(ingredient))

    @patch('core.models.uuid.uuid4')
    def test_recipie_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipie_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'upload/recipie/{uuid}.jpg')
