"""Serializers for user API view"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user Object"""

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
            'name',
        ]
        extra_kwargs = {'password': {'write_only': True, 'min_length' : 8}}

    def create(self, validated_data):
        """Create and Return a user with encrypted Password"""
        return get_user_model().objects.create(**validated_data)
