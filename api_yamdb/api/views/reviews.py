from rest_framework import viewsets, pagination, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend


from reviews.models import Category, Genre, Title
from api.serializers.reviews import (
    CategorySerializer, GenreSerializer, TitleReadSerializers,
    TitleWriteSerializers
)
from api.viewsets import CategoryGenreViewSet
from api.filters import TitleFilter


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializers
        return TitleWriteSerializers
