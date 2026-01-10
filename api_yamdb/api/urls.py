from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.reviews import (
    CategoryViewSet, GenreViewSet, TitleViewSet
)


router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
