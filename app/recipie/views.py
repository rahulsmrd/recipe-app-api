'''
Views for Recipie App
'''

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description="Comma separated list of Tag ids to filter"
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description="Comma separated list of ingredient ids to filter"
            )
        ]
    )
)
class RecipieViewSets(viewsets.ModelViewSet):
    """View for manage for recipie APIs"""

    serializer_class = serializers.RecipieDetailSerializer
    queryset = Recipie.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def _params_to_ints(self, params):
        '''Converts string parameters to integers'''
        return [int(str_id) for str_id in params.split(',')]

    def get_queryset(self):
        """Retrive Recipies for authenticated users"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_by',
                OpenApiTypes.INT, enum=[1, 0],
                description="Filter by items assigned to Recipies"
            )
        ]
    )
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipie__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseRecipieAttrViewSet):
    """Manage Tags in database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipieAttrViewSet):
    """Manage Ingredients in databse"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
