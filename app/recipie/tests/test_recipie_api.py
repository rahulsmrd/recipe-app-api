"""
Tests for Recipie API
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipie, Tag, Ingredient
from recipie.serializers import RecipieSerializer, RecipieDetailSerializer


RECIPIE_URL = reverse("recipie:recipie-list")


def detail_url(recipie_id):
    """Create and return recipie detail URL"""
    return reverse("recipie:recipie-detail", kwargs={'pk': recipie_id})


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_recipie(user, **params):
    """
    Create and return a sample Recipie
    """
    defaults = {
        'title': 'Sample Recipie Title',
        'time_minutes': 22,
        'price': Decimal('50.25'),
        'description': 'Sample Recipie Description',
        'link': 'someLink.html',
    }
    defaults.update(params)
    recipie = Recipie.objects.create(
        user=user,
        **defaults
    )

    return recipie


class PublicRecipieAPITests(TestCase):
    """
    Tests for Unauthenticated Users
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Tests Auth Required to call API"""
        res = self.client.get(RECIPIE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipieAPITests(TestCase):
    """Tests for Authorized Users"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@gmail.com',
            password='testpassword123',)
        self.client.force_authenticate(self.user)

    def test_retrive_recipie(self):
        """Test to get Recipie List"""
        create_recipie(user=self.user)
        create_recipie(user=self.user)

        res = self.client.get(RECIPIE_URL)

        recipies = Recipie.objects.all().order_by('-id')
        serializer = RecipieSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipie_list_limited_to_user(self):
        """Test list of recipies is limited to authenticated user"""

        other_user = create_user(
            email='other@example.com',
            password='testpassword123'
        )

        create_recipie(self.user)
        create_recipie(other_user)

        res = self.client.get(RECIPIE_URL)

        recipies = Recipie.objects.filter(user=self.user)
        serializer = RecipieSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_get_recipie_detail(self):
        """Test for Recipie Detail View"""
        recipie = create_recipie(self.user)

        url = detail_url(recipie.id)
        res = self.client.get(url)

        serializer = RecipieDetailSerializer(recipie)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_create_recipie(self):
        """Test Create Recipie"""
        payload = {
            "title": "Test Title",
            "price": Decimal("5.23"),
            "time_minutes": 30
        }

        res = self.client.post(RECIPIE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipie = Recipie.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipie, k), v)

        self.assertEqual(recipie.user, self.user)

    def test_partial_updtae(self):
        """Test partial update on Recipie"""

        original_link = "originallink.com"
        recipie = create_recipie(
            user=self.user,
            title='Test Title',
            link=original_link,
            )
        payload = {
            'title': "New title",
            }
        url = detail_url(recipie.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipie.refresh_from_db()
        self.assertEqual(recipie.title, payload['title'])
        self.assertEqual(recipie.link, original_link)
        self.assertEqual(recipie.user, self.user)

    def test_full_update(self):
        """Test full update of Recipie """

        recipie = create_recipie(
            user=self.user,
            title='some title',
            link='someLink.com',
            description='some description'
        )

        payload = {
            'title': 'new title',
            'description': 'New description',
            'link': 'new link',
            'time_minutes': 30,
            'price': Decimal("55.33")
        }

        url = detail_url(recipie.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipie.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipie, k), v)
        self.assertEqual(recipie.user, self.user)

    def test_update_user_return_error(self):
        """Test updating user returns an error"""

        new_user = create_user(
            email='example@gmail.com',
            password='testpass123456'
        )
        recipie = create_recipie(user=self.user)

        payload = {
            'user': new_user,
        }

        url = detail_url(recipie.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipie.refresh_from_db()
        self.assertEqual(recipie.user, self.user)

    def test_delete_reciepie(self):
        """Delete Reciepie from"""

        recipie = create_recipie(user=self.user)

        url = detail_url(recipie.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipie.objects.filter(id=recipie.id).exists())

    def test_delete_other_user_recipie_error(self):
        """Test trying to delete another users recipie raises error."""

        new_user = create_user(
            email='newuser@example.com',
            password='TestPassword123'
        )
        recipie = create_recipie(user=new_user)

        url = detail_url(recipie.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipie.objects.filter(id=recipie.id).exists())

    def test_create_recipie_with_new_tags(self):
        """Test creating a Recipie with new tags"""

        payload = {
            'title': 'Indian Prawn curry',
            'time_minutes': 30,
            'price': Decimal('50.00'),
            'tags': [
                {'name': 'Indian'},
                {'name': 'prawn'},
                {'name': 'curry'},
            ]
        }

        res = self.client.post(RECIPIE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipies = Recipie.objects.filter(user=self.user)

        self.assertEqual(recipies.count(), 1)

        recipie = recipies[0]

        self.assertEqual(recipie.tags.count(), 3)

        for tag in payload['tags']:
            exists = recipie.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()

            self.assertTrue(exists)

    def test_create_recipie_with_existing_tags(self):
        """Test creating Tags with existing tags"""
        tag_indian = Tag.objects.create(name='Indian', user=self.user)
        payload = {
            'title': 'Pongal',
            'time_minutes': 30,
            'price': Decimal('10.25'),
            'tags': [{'name': 'Indian'}, {'name': 'Pongal'}]
        }

        res = self.client.post(RECIPIE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipies = Recipie.objects.filter(user=self.user)
        self.assertEqual(recipies.count(), 1)

        recipie = recipies[0]
        self.assertEqual(recipie.tags.count(), 2)
        self.assertIn(tag_indian, recipie.tags.all())

        for tag in payload['tags']:
            exists = recipie.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()

            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating Tag on update Recipie"""
        recipie = create_recipie(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}

        url = detail_url(recipie.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipie.tags.all())

    def test_update_recipie_assign_tag(self):
        """Test assigning Existing tag to Recipie while updating it."""
        tag_breakFast = Tag.objects.create(user=self.user, name='Breakfast')

        recipie = create_recipie(user=self.user)
        url = detail_url(recipie.id)

        recipie.tags.add(tag_breakFast)
        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

        payload = {
            'tags': [{'name': 'Lunch'}]
        }

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipie.tags.all())
        self.assertNotIn(tag_breakFast, recipie.tags.all())

    def test_clear_recipie_tags(self):
        """Test clearing all Tags from Recipie"""

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        recipie = create_recipie(user=self.user)
        recipie.tags.add(tag_lunch)
        url = detail_url(recipie.id)

        payload = {
            'tags': []
        }

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipie.tags.count(), 0)

    def test_create_recipie_with_new_ingrendents(self):
        """Test creating a new recipie with new ingrendents"""
        payload = {
            'title': 'recipie title',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'ingredients': [{'name': 'ingredient1'}, {'name': 'ingredient2'}, ]
        }

        res = self.client.post(RECIPIE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipies = Recipie.objects.filter(user=self.user)

        self.assertEqual(recipies.count(), 1)
        recipie = recipies[0]
        self.assertEqual(recipie.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipie.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()

            self.assertTrue(exists)

    def test_create_recipie_with_exixting_ingredient(self):
        """Test creating a recipie with an existing ingredient"""
        ingredient = Ingredient.objects.create(
            name='ingredient',
            user=self.user
        )
        payload = {
            'title': 'recipie title',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'ingredients': [{'name': 'ingredient'}, {'name': 'ingredient2'}, ]
        }

        res = self.client.post(RECIPIE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipies = Recipie.objects.filter(user=self.user)

        self.assertEqual(recipies.count(), 1)
        recipie = recipies[0]
        self.assertEqual(recipie.ingredients.count(), 2)
        self.assertIn(ingredient, recipie.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipie.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()

            self.assertTrue(exists)

    def test_update_ingredients_on_update(self):
        """Test updating existing ingredient on recipe update"""

        recipie = create_recipie(self.user)
        payload = {
            'ingredients': [{'name': 'lemon'}]
        }

        url = detail_url(recipie.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient = Ingredient.objects.get(
            user=self.user,
            name='lemon',
        )

        self.assertIn(ingredient, recipie.ingredients.all())

    def test_update_recipie_assign_ingredient(self):
        '''Test assigning existing ingredient when updating recipe'''

        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='lemon',
        )
        recipie = create_recipie(self.user)
        recipie.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='coconut',
        )

        payload = {
            'ingredients': [{'name': 'coconut'}]
        }

        url = detail_url(recipie.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(ingredient2, recipie.ingredients.all())
        self.assertNotIn(ingredient1, recipie.ingredients.all())

    def test_clear_recipie_ingredients(self):
        '''Test clearing recipie ingredients'''

        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='lemon',
        )
        recipie = create_recipie(self.user)
        recipie.ingredients.add(ingredient1)

        payload = {
            'ingredients': []
        }

        url = detail_url(recipie.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipie.ingredients.count(), 0)
