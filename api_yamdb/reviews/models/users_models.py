from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb import settings

from reviews.validators import check_username


MIN_RATING = 1
MAX_RATING = 10
MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 100
MAX_ROLE_LENGTH = 12

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
]


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[check_username],
    )

    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )

    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )

    bio = models.TextField(
        verbose_name='Инфо',
        blank=True,
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_NAME_LENGTH,
        blank=True,
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_NAME_LENGTH,
        blank=True,
    )

    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
    )

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Группы',
        blank=True,
        related_name="custom_user_groups",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Пользовательские права',
        blank=True,
        related_name="custom_user_permissions",
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER
