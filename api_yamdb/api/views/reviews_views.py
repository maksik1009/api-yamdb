from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404


from reviews.models import Category, Genre, Title, Review
from api.serializers.reviews_serializers import (
    CategorySerializer, GenreSerializer, TitleReadSerializers,
    TitleWriteSerializers, CommentSerializer, ReviewSerializer
)
from api.viewsets import CategoryGenreViewSet
from api.filters import TitleFilter
from api.permissions import IsAdminOrReadOnly


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializers
        return TitleWriteSerializers


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
