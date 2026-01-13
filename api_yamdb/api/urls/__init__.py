from django.urls import path, include

from . import reviews_urls, users_urls


urlpatterns = [
    path('', include(reviews_urls)),
    path('', include(users_urls)),
]
