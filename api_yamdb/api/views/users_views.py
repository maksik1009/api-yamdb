import random

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, filters, serializers
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .permissions import IsAdmin
from .serializers import (
    SignupSerializer, TokenObtainSerializer, UserSerializer)
from django.shortcuts import get_object_or_404
from api.serializers import (
    CommentSerializer, TitleSerializer, ReviewSerializer)
from reviews.models import Review, Title

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
            raise serializers.ValidationError({
                'username': [EMAIL_ERROR_MESSAGE]
            })

        elif user_by_email:
            raise serializers.ValidationError({
                'email': [EMAIL_ALIEN_ERROR_MESSAGE]
            })

        else:
            user = User.objects.create(username=username, email=email)

        confirmation_code = ''.join(
            random.choices(
                settings.CONFIRMATION_CODE_CHARS,
                k=settings.CONFIRMATION_CODE_LENGTH
            ))
        user.confirmation_code = confirmation_code
        user.save(update_fields=['confirmation_code'])

        send_mail(
            subject='Код подтверждения YaMDb',
            message=(
                f'Ваш код подтверждения: {confirmation_code}\n'
                'Используйте код для получения токена.'
            ),
            from_email='noreply@yamdb.mail.ru',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {'email': email, 'username': username}
        )


class TokenObtainView(APIView):
    """Получение JWT-токена путем предоставления confirmation_code"""
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)

        if len(confirmation_code) != settings.CONFIRMATION_CODE_LENGTH:
            raise ValidationError('Неправильная длина кода подтверждения.')
        elif confirmation_code != user.confirmation_code:
            raise ValidationError('Неверный код подтверждения.')

        user.confirmation_code = ''
        user.save(update_fields=['confirmation_code'])

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserPagination(PageNumberPagination):
    """Класс для постраничной навигации"""
    page_size = 10


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    pagination_class = UserPagination
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'role']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'me' or (
            self.request.method == 'DELETE'
            and self.request.path.endswith('/me/')
        ):
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

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


class TitleViewSet(viewsets.ModelViewSet):
    """Представления для объектов Title"""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Представления для объектов Comment"""
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    """Представления для объектов Review"""
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
