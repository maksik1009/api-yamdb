from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, Comment, Review, Title)
from reviews.validators import UsernameValidator

User = get_user_model()


class SignupSerializer(UsernameValidator, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH
    )
    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH
    )

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
            'password': {'write_only': True},  # Поле пароля доступно только для записи
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


class UserMeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Title


class BaseReviewCommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        abstract = True
        fields = ('id', 'text', 'author', 'pub_date')


class CommentSerializer(BaseReviewCommentSerializer):
    class Meta(BaseReviewCommentSerializer.Meta):
        model = Comment
        read_only_fields = ('review',)


class ReviewSerializer(BaseReviewCommentSerializer):
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta(BaseReviewCommentSerializer.Meta):
        model = Review
        fields = BaseReviewCommentSerializer.Meta.fields + ('score',)
        read_only_fields = ('title',)

    def validate(self, attrs):
        user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        existing_review = title.reviews.filter(author=user).exists()
        if existing_review and self.context['request'].method == 'POST':
            raise ValidationError("Вы уже оставили отзыв.")
        return attrs
