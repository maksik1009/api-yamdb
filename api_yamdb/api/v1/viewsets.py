from rest_framework import filters, mixins, pagination, viewsets

from .permissions import IsAdminOrReadOnly


class CategoryGenreViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin
):
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (
        IsAdminOrReadOnly,
    )
