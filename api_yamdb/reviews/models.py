from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import (
    unicode_validator,
    validate_username_restricted,
    validate_year
)

MIN_RATING = 1
MAX_RATING = 10
MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 100
MAX_ROLE_LENGTH = 12
MAX_NAME_FIELD_LENGTH = 256
MAX_SLUG_FIELD_LENGTH = 50


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    role = models.CharField(
        'Роль',
        max_length=MAX_ROLE_LENGTH,
        choices=Role.choices,
        default=Role.USER,
    )

    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[unicode_validator, validate_username_restricted],
    )

    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', 'email', 'id')

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == self.Role.ADMIN
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Genre(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_FIELD_LENGTH,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_FIELD_LENGTH,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанра'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_FIELD_LENGTH,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_FIELD_LENGTH,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_FIELD_LENGTH,
        verbose_name='Название'
    )
    year = models.SmallIntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска',
        db_index=True
    )

    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-year',)
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывы."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        verbose_name='Ревьюер',
        on_delete=models.CASCADE)
    text = models.TextField(
        verbose_name='Отзыв'
    )
    score = models.SmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(MIN_RATING), MaxValueValidator(MAX_RATING)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return (
            f'Отзыв от {self.author} '
            f'на произведение {self.title.name}.'
        )


class Comment(models.Model):
    """Модель комментарии."""

    review = models.ForeignKey(
        Review,
        verbose_name='Комментарий',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        verbose_name='Комментатор',
        on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            f'Комментарий от {self.author} '
            f'на отзыв {self.review.author} '
            f'к произведению {self.review.title.name}.'
        )
