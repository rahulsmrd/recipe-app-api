"""
Test for Ingredient API
"""


from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipie
from recipie.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipie:ingredient-list')


def ingredient_detail(ingredient_id):
    """Returns the url of the ingredient"""
    return reverse('recipie:ingredient-detail', args=[ingredient_id])


def create_user(email='email@test.com', password='testpassword'):
    """Create a new user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientApiTest(TestCase):
    """Test Unauthenticated requests"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for getting list of Ingredients"""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test Authenticate API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient(self):
        """Test retrieve list of Ingredient"""

        Ingredient.objects.create(user=self.user, name='Ingredient1')
        Ingredient.objects.create(user=self.user, name='Ingredient2')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredient limited to authenticate user"""

        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='ingredient2')

        ingredient = Ingredient.objects.create(
            user=self.user,
            name='ingredient'
        )

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_ingredient_update(self):
        """Test updating an existing ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='ingredient'
        )
        payload = {'name': "ingredient22"}
        url = ingredient_detail(ingredient.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='ingredient'
        )

        url = ingredient_detail(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)

        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipie(self):
        '''Test listing ingredients by those assigned to recipies'''
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='ingredient1'
        )

        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='ingredient2'
        )

        recipie = Recipie.objects.create(
            title='Sample Recipie Title',
            time_minutes=22,
            price=Decimal('50.25'),
            user=self.user
        )

        recipie.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='ingredient1'
        )

        Ingredient.objects.create(
            user=self.user,
            name='ingredient2'
        )

        recipie1 = Recipie.objects.create(
            title='Sample Recipie Title',
            time_minutes=22,
            price=Decimal('50.25'),
            user=self.user
        )
        recipie1.ingredients.add(ingredient1)

        recipie2 = Recipie.objects.create(
            title='Sample Recipie Title2',
            time_minutes=2,
            price=Decimal('0.25'),
            user=self.user
        )
        recipie2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
