import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from reviews.validators import check_username

from api_yamdb import settings


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


class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанра'


class Category(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    year = models.IntegerField(
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(datetime.date.today().year)
        ],
        verbose_name='Год выпуска'
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
        ordering = ['-year']
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
        ordering = ['-pub_date']
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
        ordering = ['-pub_date']

    def __str__(self):
        return (
            f'Комментарий от {self.author} '
            f'на отзыв {self.review.author} '
            f'к произведению {self.review.title.name}.'
        )
