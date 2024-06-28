'''
Views for Recipie App
'''

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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

        if self.action == 'upload_image':
            return serializers.RecipieImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipie"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload a new Image to the Recipie"""
        recipie = self.get_object()
        serializer = self.get_serializer(recipie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
