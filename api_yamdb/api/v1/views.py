from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly, IsOwnerOrReadOnly
)
from .serializers import (
    SignupSerializer, TokenObtainSerializer,
    UserSerializer
)
from .viewsets import CategoryGenreViewSet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title

from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleWriteSerializer, TitleReadSerializer)

USERNAME_ERROR_MESSAGE = 'Пользователь с таким username уже зарегистрирован'
EMAIL_ERROR_MESSAGE = 'Такой email уже занят другим пользователем'
USERNAME_EMAIL_MISMATCH = 'username и email принадлежат разным аккаунтам'
EMAIL_ALIEN_ERROR_MESSAGE = 'Чужой email.'


User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if (user_by_username and user_by_email
                and user_by_username != user_by_email):
            raise serializers.ValidationError({
                'username': [USERNAME_ERROR_MESSAGE],
                'email': [EMAIL_ALIEN_ERROR_MESSAGE]
            })

        if (
            user_by_username
            and user_by_email
            and user_by_username == user_by_email
        ):
            user = user_by_username
        elif user_by_username:
            raise serializers.ValidationError(
                {'username': [EMAIL_ERROR_MESSAGE]})
        elif user_by_email:
            raise serializers.ValidationError(
                {'email': [EMAIL_ALIEN_ERROR_MESSAGE]})
        else:
            user = User.objects.create(username=username, email=email)

        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    """Получение JWT-токена путем предоставления confirmation_code"""
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError({
                'confirmation_code': 'Неверный код подтверждения'
            })

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'role']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    permission_classes = (permissions.IsAdminUser,)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsOwnerOrReadOnly]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
