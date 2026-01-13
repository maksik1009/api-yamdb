from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers


from reviews.models import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH)
from reviews.validators import UsernameValidator


User = get_user_model()


class SignupSerializer(UsernameValidator, serializers.Serializer):
    username = serializers.CharField(
        required=True, max_length=MAX_USERNAME_LENGTH)
    email = serializers.EmailField(
        required=True, max_length=MAX_EMAIL_LENGTH)

    def create(self, validated_data):
        """Переопределённая логика создания пользователя"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH, required=True)
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH, required=True)


class UserSerializer(UsernameValidator, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)
