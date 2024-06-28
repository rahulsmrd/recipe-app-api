"""
Tests for Tag API's
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipie
from recipie.serializers import TagSerializer

TAG_URL = reverse("recipie:tag-list")


def detailURL(tag_id):
    """Create and return Tag Detail URL."""
    return reverse("recipie:tag-detail", args=[tag_id, ])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a User"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Tests for Unauthorised User"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test Auth is required for retriving tags"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Test Authenticate Users"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retriving List of tags"""

        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test lsit of tags related to authenticate user"""

        user2 = create_user(email='user2@example.com', password='password')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Vegan')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test Update Tag"""

        tag = Tag.objects.create(user=self.user, name="After Dinner")
        paylaod = {
            'name': 'Dessert'
        }
        url = detailURL(tag.id)

        res = self.client.patch(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, paylaod['name'])

    def test_delete_tag(self):
        """Test deleting tag"""

        tag = Tag.objects.create(user=self.user, name="After Dinner")

        url = detailURL(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipie(self):
        '''Test listing tags by those assigned to recipies'''
        tag1 = Tag.objects.create(
            user=self.user,
            name='tag1'
        )

        tag2 = Tag.objects.create(
            user=self.user,
            name='ingredient2'
        )

        recipie = Recipie.objects.create(
            title='Sample Recipie Title',
            time_minutes=22,
            price=Decimal('50.25'),
            user=self.user
        )

        recipie.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list"""
        tag1 = Tag.objects.create(
            user=self.user,
            name='tag1'
        )

        Tag.objects.create(
            user=self.user,
            name='tag2'
        )

        recipie1 = Recipie.objects.create(
            title='Sample Recipie Title',
            time_minutes=22,
            price=Decimal('50.25'),
            user=self.user
        )
        recipie1.tags.add(tag1)

        recipie2 = Recipie.objects.create(
            title='Sample Recipie Title2',
            time_minutes=2,
            price=Decimal('0.25'),
            user=self.user
        )
        recipie2.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
