"""
Seralizers for Recipie APIs
"""

from rest_framework import serializers
from core.models import Recipie, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag View"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient View"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipieSerializer(serializers.ModelSerializer):
    """Serializer for Recipie"""

    tags = TagSerializer(many=True, required=False)

    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipie
        fields = [
            "id", 'title', 'time_minutes',
            'price', 'link', 'tags', 'ingredients', 'image'
        ]
        read_only_fields = ['id', ]

    def _get_or_create_tags(self, tags, recipie):
        """Handlng Getting or Creating Tags as Needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipie.tags.add(tag_obj)
            recipie.save()

    def _get_or_create_ingredient(self, ingredients, recipie):
        """Handle creating or updating an ingredient from a recipe"""

        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipie.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        '''Custom create method for Recipie Serializer '''
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipie = Recipie.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipie)
        self._get_or_create_ingredient(ingredients, recipie)
        return recipie

    def update(self, instance, validated_data):
        """update recipie"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredient(ingredients, instance)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class RecipieDetailSerializer(RecipieSerializer):
    """Serializer for Recipie Detail View"""

    class Meta(RecipieSerializer.Meta):
        fields = RecipieSerializer.Meta.fields + ['description']


class RecipieImageSerializer(serializers.ModelSerializer):
    """Serializer for Recipie Images"""
    class Meta:
        model = Recipie
        fields = ['id', 'image']
        extra_kwargs = {'image': {'required': 'True'}}
