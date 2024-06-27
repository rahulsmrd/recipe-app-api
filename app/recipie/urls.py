"""URL mappings for Recipie APP"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter
from recipie.views import RecipieViewSets, TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('recipies', RecipieViewSets)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

app_name = 'recipie'

urlpatterns = [
    path('', include(router.urls)),
]
