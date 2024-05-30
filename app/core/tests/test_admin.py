"""
Tests for Admin
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Admin Tests"""

    def setUp(self):
        """Create user client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@emaple.com',
            'adminuser123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='exampleuser123',
            name='Admiin User'
        )

    def test_user_list(self):
        """Test for users listed on Page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        """adding extra fields in user model"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)

    def test_create_user_page(self):
        """Tests to create a user page"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)
