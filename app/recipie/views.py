'''
Views for Recipie App
'''

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipie,
    Tag,
    Ingredient,
)
from recipie import serializers


class RecipieViewSets(viewsets.ModelViewSet):
    """View for manage for recipie APIs"""

    serializer_class = serializers.RecipieDetailSerializer
    queryset = Recipie.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """Retrive Recipies for authenticated users"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the Serializer class for a request"""

        if self.action == 'list':
            return serializers.RecipieSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipie"""
        serializer.save(user=self.request.user)


class BaseRecipieAttrViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    """Base ViewSet for recipie attributes"""
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        """Filter QuerySet based on Login User"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipieAttrViewSet):
    """Manage Tags in database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipieAttrViewSet):
    """Manage Ingredients in databse"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
