from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.validators import unicode_validator, validate_username_restricted
from reviews.models import (
    Category, Comment, Genre, Review, Title,
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH
)

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[unicode_validator, validate_username_restricted]
    )
    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        errors = {}

        if User.objects.filter(
            username=username
        ).exclude(email=email).exists():
            errors['username'] = 'Это имя уже занято другим пользователем.'

        if User.objects.filter(
            email=email
        ).exclude(username=username).exists():
            errors['email'] = 'Эта почта уже занята другим пользователем.'

        if errors:
            raise serializers.ValidationError(errors)

        return data


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[unicode_validator, validate_username_restricted]
    )
    confirmation_code = serializers.CharField(
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'pub_date', 'score')

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method != 'POST':
            return attrs
        user = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=user, title_id=title_id).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение.')
        return attrs
