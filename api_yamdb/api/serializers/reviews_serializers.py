from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Comment, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializers(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)

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
        read_only_fields = ('title',)

    def validate(self, attrs):
        user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        existing_review = title.reviews.filter(author=user).exists()
        if existing_review and self.context['request'].method == 'POST':
            raise ValidationError("Вы уже оставили отзыв.")
        return attrs
