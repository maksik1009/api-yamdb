from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.validators import unicode_validator, validate_username_not_me
from reviews.models import (Category, Comment, Genre, Review, Title)

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[unicode_validator, validate_username_not_me]
    )
    email = serializers.EmailField(required=True, max_length=254)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" неподходит')
        return value


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[UnicodeUsernameValidator()]
    )
    confirmation_code = serializers.CharField(
        required=True
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено.'
            )
        return value


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


class TitleSerializers(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializers(TitleSerializers):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )


class TitleReadSerializers(TitleSerializers):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


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

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method != 'POST':
            return attrs
        user = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=user, title_id=title_id).exists():
            raise ValidationError("Вы уже оставили отзыв на это произведение.")
        return attrs
