from rest_framework import serializers

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            # 'rating',
            'description',
            'genre',
            'category'
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
